# INSTRUCCIONES DE SUBMISSION (Carlo — 10 minutos)

Bounty: Develop Solana Ecosystem Auto-Updating Report & Interactive Dashboard
Sponsor: Superteam Canada (verificado) · Premio: 6 × 250 USDG
Deadline: 2026-09-01 03:59 UTC (~2 días) · 13 submissions ya
HUMAN_ONLY: el trabajo es del agente; la submission sale de TU cuenta.

## Paso 1 — Publica el repo en tu GitHub (5 min)
```powershell
cd C:\Users\carlo\AUTARCH\workspace\solana-ecosystem-dashboard
git init; git add .; git commit -m "Solana ecosystem live report + dashboard"
# crea el repo vacio en github.com/new (publico, nombre: solana-ecosystem-dashboard)
git remote add origin https://github.com/<TU_USUARIO>/solana-ecosystem-dashboard.git
git push -u origin main
```

## Paso 2 — Activa GitHub Pages (2 min)
Repo → Settings → Pages → Branch: `main` / root → Save.
URL queda: https://<TU_USUARIO>.github.io/solana-ecosystem-dashboard/
El workflow hourly ya queda activo (pestaña Actions → habilitar si lo pide).

## Paso 3 — Sube a Superteam Earn (3 min)
1. https://earn.superteam.fun/listing/develop-solana-ecosystem-auto-updating-report-and-interactive-dashboard/
2. Submit con tu cuenta. Texto sugerido:

---
**Solana Ecosystem Live Report & Dashboard**

Auto-updating dashboard that pulls everything client-side on every load
(Solana RPC: getEpochInfo/getVoteAccounts/getSupply/getRecentPerformanceSamples;
DeFiLlama TVL + stablecoins; CoinGecko price) + an hourly-regenerated
markdown snapshot via GitHub Actions. Zero servers, zero API keys,
per-metric source citations, fail-soft panels.

Live: https://<TU_USUARIO>.github.io/solana-ecosystem-dashboard/
Snapshot: https://github.com/<TU_USUARIO>/solana-ecosystem-dashboard/blob/main/REPORT.md
---

## Notas honestas
- El dashboard usa Chart.js por CDN y endpoints publicos con CORS.
- Si un panel dice "unreachable" al abrirlo, refresca: rotamos entre 3 RPCs.
- El workflow hourly puede tardar ~1h en correr por primera vez; puedes
  forzarlo en Actions → hourly-report → Run workflow.
