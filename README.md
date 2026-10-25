<p align="center">
  <a href="https://fatumon.com">
    <img src="assets/logo.svg" alt="Fatumon" width="420">
  </a>
</p>

<p align="center">
  <img alt="exchanges" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.exchanges&label=exchanges&color=9BE8FF">
  <img alt="trading pairs" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.coins&label=trading%20pairs&color=e0bf88">
  <img alt="data" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.data_gb&label=data&suffix=%20GB&color=4ADE80">
  <img alt="signals" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.signals&label=signals&color=F472B6">
  <img alt="anomalies" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.anomalies&label=anomalies&color=A78BFA">
</p>

<h1 align="center">Fatumon</h1>

<p align="center">
  Собственный ИИ, который находит рабочие торговые стратегии.<br>
  <em>Our own AI that finds trading strategies that work.</em>
</p>

<p align="center">
  <a href="https://fatumon.com"><strong>fatumon.com</strong></a> ·
  <a href="https://t.me/fatumon">Telegram</a> ·
  <a href="https://x.com/fatumon_token">X</a> ·
  <a href="https://github.com/fatumon-token">GitHub</a>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-e0bf88.svg"></a>
  <img alt="Static site" src="https://img.shields.io/badge/site-static%20%C2%B7%20no%20build-060912.svg">
  <img alt="Languages" src="https://img.shields.io/badge/lang-RU%20%7C%20EN-3B82F6.svg">
</p>

---

**RU.** Fatumon — исследовательская платформа: рыночные данные с 8 бирж, проверяемые прогнозы, игра на прогнозах, токен доступа. Этот репозиторий — публичный сайт проекта.

**EN.** Fatumon is a research platform: market data from 8 exchanges, verifiable forecasts, a forecasting game, an access token. This repository is the project's public website.

> Это исследовательская платформа, не финансовый совет. / This is a research platform, not financial advice.

## Overview

The site is a plain static website: no framework, no build step, no server. It is served by GitHub Pages and works both at the repository path (`/fatumon-site/`) and at the root of a custom domain, because every path is relative.

- **Pages:** Home · About · How it works · Ecosystem · Roadmap · Token · Contact
- **Languages:** Russian and English, switched on the client (`?lang=ru|en`, remembered in `localStorage`)
- **Live counters:** read from [`stats.json`](stats.json), refreshed by a scheduled export (see below)
- **Design:** dark space background with drifting glass panels and gold accents

## Repository structure

```
.
├── index.html            Home
├── about/                About
├── how/                  How it works
├── ecosystem/            Ecosystem (products and their status)
├── roadmap/              Roadmap (phases, no dates)
├── token/                Token
├── contact/              Contact
├── 404.html              Redirects to the home page, keeps ?lang
├── assets/
│   ├── style.css         Design tokens, layout, responsive rules
│   ├── app.js            i18n, navigation, stars, counters, mascot
│   ├── logo.svg          Logo
│   └── favicon.svg       Favicon
├── i18n/
│   ├── ru.json           Russian strings (flat keys)
│   └── en.json           English strings
├── stats.json            Live counters (generated, do not edit by hand)
├── tools/
│   └── check_texts.py    Stop-word check for all public texts
├── CNAME                 Custom domain for GitHub Pages
├── .nojekyll             Disable Jekyll processing on Pages
└── LICENSE               MIT
```

## Running locally

Any static file server works. With Python:

```bash
git clone https://github.com/fatumon-token/fatumon-site.git
cd fatumon-site
python -m http.server 8080
```

Then open <http://localhost:8080/>. Add `?lang=en` to force English.

## Counters (`stats.json`)

The pixel-display row on the home page (exchanges, trading pairs, GB of data, signals, anomalies in the registry) and the badges at the top of this README read `stats.json`:

```json
{
  "anomalies": 40,
  "anomalies_24h": 92,
  "coins": 476,
  "data_gb": 152,
  "exchanges": 8,
  "signals": 523,
  "updated_at": "…UTC ISO timestamp…",
  "uptime_days": 1
}
```

| key | meaning |
|---|---|
| `exchanges` | exchanges in the collector's symbol map |
| `coins` | trading pairs tracked (Binance perp + spot) |
| `data_gb` | size of the raw archive, GB |
| `signals` | rows in the open signal journal |
| `anomalies` | features in the anomaly registry (shown on the site) |
| `anomalies_24h` | anomaly events detected in the last 24 hours (exported, not shown) |
| `uptime_days` | consecutive days with complete daily data on all exchanges (exported, not shown) |
| `updated_at` | time of the export, UTC ISO |

The file is produced by an export script that runs on a schedule against the research database, commits the new `stats.json` to this repository and pushes it (`stats: <timestamp>` commits). The page fetches the file with an hourly cache-busting parameter, and re-reads it every hour and whenever the tab becomes visible again. If the file is unavailable the page falls back to the numbers embedded in the HTML. The badges are rendered by shields.io from the same file, so they show `invalid` until the first deployment.

## Adding or editing texts

1. Every visible string lives in `i18n/ru.json` and `i18n/en.json` under the same flat key (`home.hero.title`, `roadmap.p3.1`, …).
2. HTML elements reference keys with `data-i18n`, `data-i18n-html` (for inline markup) or `data-i18n-attr="attr:key"`; the Russian text inside the HTML is the no-JavaScript fallback.
3. Before committing, run the stop-word check from the repository root:

```bash
python -I tools/check_texts.py
```

It scans both dictionaries, this README and all HTML pages and exits with a non-zero code if any public text contains a forbidden word or pattern (promotional claims, dates, personal names and so on).

## Deployment

GitHub Pages serves the `main` branch from the repository root. `CNAME` points the site at the custom domain; `.nojekyll` keeps Pages from touching the files.

## Contact

- Email: [fatumon.token@gmail.com](mailto:fatumon.token@gmail.com)
- Telegram: [t.me/fatumon](https://t.me/fatumon)
- X: [x.com/fatumon_token](https://x.com/fatumon_token)
- GitHub: [github.com/fatumon-token](https://github.com/fatumon-token)

## License

[MIT](LICENSE) © Fatumon
