#!/usr/bin/env python3
"""Generate REPORT.md â€” a snapshot of the Solana ecosystem.

Stdlib only. Every metric cites its source endpoint. Fail-soft per
section: one dead source never blanks the whole report.
"""

import json
import urllib.request
from datetime import datetime, timezone

RPCS = ["https://api.mainnet-beta.solana.com",
        "https://rpc.ankr.com/solana",
        "https://solana-rpc.publicnode.com"]
_rpc_idx = 0


def rpc(method, params=None):
    global _rpc_idx
    params = params or []
    last = None
    for i in range(len(RPCS)):
        ep = RPCS[(_rpc_idx + i) % len(RPCS)]
        try:
            req = urllib.request.Request(
                ep, data=json.dumps(
                    {"jsonrpc": "2.0", "id": 1,
                     "method": method, "params": params}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                j = json.loads(r.read())
            if "error" in j:
                raise RuntimeError(j["error"].get("message", "rpc error"))
            _rpc_idx = (_rpc_idx + i) % len(RPCS)
            return j["result"]
        except Exception as e:
            last = e
    raise last  # type: ignore[misc]


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "report/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def section(title, rows):
    out = [f"\n## {title}\n"]
    if not rows:
        out.append("_source unreachable at generation time._\n")
        return "\n".join(out)
    for k, v in rows:
        out.append(f"- **{k}:** {v}")
    return "\n".join(out) + "\n"


def main():
    now = datetime.now(timezone.utc)
    parts = [
        "# Solana Ecosystem Report",
        f"\n_Generated {now.strftime('%Y-%m-%d %H:%M UTC')} â€” "
        "auto-regenerated hourly by GitHub Actions. "
        "Interactive companion: `index.html` (live client-side)._",
    ]

    # --- network ---
    rows = []
    try:
        e = rpc("getEpochInfo")
        perf = rpc("getRecentPerformanceSamples", [60]) or []
        tx = sum(s["numTransactions"] for s in perf)
        slots = sum(s["numSlots"] for s in perf)
        secs = sum(s["samplePeriodSecs"] for s in perf)
        rows += [("TPS (60-min sample)", f"{tx / secs:,.0f}" if secs else "n/a"),
                 ("Slot", f"{e['absoluteSlot']:,}"),
                 ("Block height", f"{e['blockHeight']:,}"),
                 ("Epoch", e["epoch"]),
                 ("Epoch progress",
                  f"{e['slotIndex'] / e['slotsInEpoch'] * 100:.2f}%"),
                 ("Avg slot time",
                  f"{secs / slots * 1000:.0f} ms" if slots else "n/a"),
                 ("Source", "Solana JSON-RPC (`getEpochInfo`, "
                  "`getRecentPerformanceSamples`)")]
    except Exception as exc:
        print(f"[warn] network section failed: {exc}", file=sys.stderr)
    parts.append(section("Network Performance", rows))

    # --- validators ---
    rows = []
    try:
        v = None
        # Some public RPCs return stake=0 for every validator; keep
        # rotating endpoints until we get real stake data.
        for _ in range(len(RPCS)):
            v = rpc("getVoteAccounts")
            tot_wei = sum((x.get("activatedStake") or x.get("stake") or 0) for x in
                          (v.get("current") or []) + (v.get("delinquent") or []))
            if tot_wei > 0:
                break
        current, delinq = v.get("current") or [], v.get("delinquent") or []
        allv = current + delinq
        total = sum((x.get("activatedStake") or x.get("stake") or 0) for x in allv) / 1e9
        dstake = sum((x.get("activatedStake") or x.get("stake") or 0) for x in delinq) / 1e9
        top = sorted(allv, key=lambda x: (x.get("activatedStake") or x.get("stake") or 0),
                     reverse=True)[:5]
        rows += [("Active validators", len(current)),
                 ("Delinquent", len(delinq))]
        if total > 0:
            rows += [
                ("Total stake", f"{total:,.0f} SOL"),
                ("Delinquent stake",
                 f"{dstake:,.0f} SOL ({dstake / total * 100:.2f}%)"),
                ("Top 5 by stake",
                  ", ".join((x.get("votePubkey", "")[:10] + "â€¦")
                            for x in top)),
            ]
        else:
            rows.append(("Total stake",
                         "n/a â€” RPC served no stake index"))
        rows.append(("Source", "`getVoteAccounts`"))
    except Exception as exc:
        print(f"[warn] validator section failed: {exc}", file=sys.stderr)
    parts.append(section("Validator Status", rows))

    # --- economy ---
    rows = []
    try:
        cg = get_json("https://api.coingecko.com/api/v3/simple/price"
                      "?ids=solana&vs_currencies=usd&include_24hr_change=true")
        p = cg["solana"]["usd"]
        ch = cg["solana"].get("usd_24h_change")
        rows.append(("SOL price", f"${p:,.2f}"
                     + (f" ({ch:+.2f}% / 24h)" if ch is not None else "")))
    except Exception as exc:
        print(f"[warn] price failed: {exc}", file=sys.stderr)
    try:
        chains = get_json("https://api.llama.fi/v2/chains")
        sol = next(c for c in chains if c["name"].lower() == "solana")
        prev = sol.get("tvlPrev24h") or sol.get("tvlPrevDay")
        chg = (f" ({(sol['tvl'] - prev) / prev * 100:+.2f}% / 24h)"
               if prev else "")
        rows.append(("Chain TVL", f"${sol['tvl'] / 1e9:,.2f} B{chg}"))
    except Exception as exc:
        print(f"[warn] TVL failed: {exc}", file=sys.stderr)
    try:
        st = get_json("https://stablecoins.llama.fi/stablecoinchains")
        sol = next(c for c in st if c["name"].lower() == "solana")
        usd_amt = sol["totalCirculatingUSD"]["peggedUSD"]
        rows.append(("Stablecoin supply", f"${usd_amt / 1e9:,.2f} B"))
    except Exception as exc:
        print(f"[warn] stablecoins failed: {exc}", file=sys.stderr)
    rows.append(("Sources", "CoinGecko simple/price Â· DeFiLlama "
                 "`/v2/chains` Â· DeFiLlama stablecoins"))
    parts.append(section("Economic Indicators", rows))

    # --- supply ---
    rows = []
    try:
        s = rpc("getSupply", [{"excludeNonCirculatingAccountsList": True}])
        circ = s["value"]["circulating"] / 1e9
        tot = s["value"]["total"] / 1e9
        rows += [("Circulating supply", f"{circ / 1e6:,.1f} M SOL"),
                 ("Total supply", f"{tot / 1e6:,.1f} M SOL"),
                 ("% circulating", f"{circ / tot * 100:.1f}%"),
                 ("Source", "`getSupply`")]
    except Exception as exc:
        print(f"[warn] supply failed: {exc}", file=sys.stderr)
    parts.append(section("Supply", rows))

    with open("REPORT.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts) + "\n")
    print("REPORT.md written")


if __name__ == "__main__":
    import sys
    sys.exit(main())
