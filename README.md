# Solana Ecosystem — Auto-Updating Report & Interactive Dashboard

Live, self-refreshing view of the Solana network: performance, validators,
economy and supply. Built for the Superteam Canada bounty
*"Develop Solana Ecosystem Auto-Updating Report & Interactive Dashboard"*.

## What makes it "auto-updating"

Two complementary mechanisms, zero servers:

1. **`index.html` (interactive dashboard)** — queries public, keyless
   endpoints **directly from the browser** on every page load, then
   refreshes itself every 60 seconds. Open the file (or its GitHub Pages
   URL) and you are always looking at current data. Nothing cached,
   nothing stale.

2. **`REPORT.md` (markdown snapshot)** — regenerated **hourly** by a
   GitHub Actions workflow (`.github/workflows/hourly.yml`) so
   programmatic consumers always have a fresh, diffable snapshot in-repo.
   The workflow is stdlib-only (`generate_report.py` needs no pip install).

## Data sources (all public, keyless, cited per metric)

| Metric | Source |
|---|---|
| TPS, slot, block height, epoch progress, slot time | Solana JSON-RPC `getEpochInfo`, `getRecentPerformanceSamples` |
| Active/delinquent validators, stake distribution, Nakamoto coefficient | Solana JSON-RPC `getVoteAccounts` |
| Supply (circulating / total) | Solana JSON-RPC `getSupply` |
| RPC health | `getHealth` |
| SOL price + 24h change | CoinGecko `simple/price` |
| Chain TVL (+24h) | DeFiLlama `/v2/chains` |
| Stablecoin supply | DeFiLlama stablecoins API |

The dashboard rotates across multiple RPC endpoints and re-queries when a
source returns empty stake indexes or errors — a dead endpoint degrades
one panel, never the whole report.

## Run it

```bash
# dashboard: just open index.html in any browser
# report:
python generate_report.py   # writes REPORT.md (stdlib only)
```

Deploy on GitHub Pages (recommended): push this repo, enable Pages on the
root — the dashboard becomes a URL that is itself always live.

## Design notes

- **Fail-soft per panel**: every source failure is contained; the rest of
  the report keeps working with an explicit `_unreachable_` marker instead
  of silently hiding data.
- **No silent estimates**: numbers come straight from cited endpoints;
  derived values (Nakamoto coefficient approximation = top-N validators
  holding >1/3 of stake) are labeled as such in the UI.
- **Honest units**: validator stakes shown in SOL (`activatedStake`
  lamports ÷ 10⁹).
