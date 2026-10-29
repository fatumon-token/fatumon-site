<p align="center">
  <a href="https://fatumon.com">
    <img src="assets/brand/logo.svg" alt="Fatumon" width="160">
  </a>
</p>

<p align="center">
  <img alt="exchanges" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.exchanges&label=exchanges&color=9BE8FF">
  <img alt="trading pairs" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.coins&label=trading%20pairs&color=e0bf88">
  <img alt="data" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.data_gb&label=data&suffix=%20GB&color=4ADE80">
  <img alt="signals" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.signals&label=signals&color=F472B6">
  <img alt="anomalies" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.anomalies&label=anomalies&color=A78BFA">
  <img alt="anomalies 24h" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffatumon-token.github.io%2Ffatumon-site%2Fstats.json&query=%24.anomalies_24h&label=anomalies%2024h&color=ffb347">
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

- **Pages:** Home · About · How it works · Ecosystem · Games · Roadmap · Token · Contact · Terms · Privacy; Journal is reachable by direct link only (not in the menu, `noindex`)
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
├── games/                Games: the Telegram mini app, its games, candle heroes, games roadmap
├── journal/              Signal journal of strategy S1 (unlisted, noindex; reads journal.json)
├── roadmap/              Roadmap (phases, no dates)
├── token/                Token
├── contact/              Contact
├── 404.html              Redirects to the home page, keeps ?lang
├── terms/                Terms of Service (RU/EN blocks)
├── privacy/              Privacy Policy (RU/EN blocks)
├── assets/
│   ├── fonts/            Self-hosted woff2 fonts + LICENSES.md
│   ├── style.css         Design tokens, @font-face, layout, responsive rules
│   ├── app.js            i18n, navigation, stars, counters, mascot
│   ├── brand/            Logo, favicon, avatars, OG image (see Brand)
│   └── games/            Art for the Games page, copied from the game
│       ├── heroes/       Candle hero sprites (hammer, doji, marubozu, engulfing, harami), webp
│       └── icons/        Game icons icon_<game id>.webp + forecast / tree / rating / friends icons
├── i18n/
│   ├── ru.json           Russian strings (flat keys)
│   └── en.json           English strings
├── config.json           Hand-edited numbers used in strings, e.g. `{game.languages}`
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

The pixel-display row on the home page (exchanges, trading pairs, GB of data, signals, anomalies in the registry, anomalies in the last 24 hours) and the badges at the top of this README read `stats.json`:

```json
{
  "anomalies": 40,
  "anomalies_24h": 108,
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
| `signals` | all signals recorded by the scanner and the signal journals |
| `anomalies` | features in the anomaly registry (shown on the site) |
| `anomalies_24h` | anomaly events detected in the last 24 hours (rebuilt hourly) |
| `uptime_days` | consecutive days with complete daily data on all exchanges (exported, not shown) |
| `updated_at` | time of the export, UTC ISO |

The file is produced by an export script that runs on a schedule against the research database, commits the new `stats.json` to this repository and pushes it (`stats: <timestamp>` commits). The page fetches the file with an hourly cache-busting parameter, and re-reads it every hour and whenever the tab becomes visible again. If the file is unavailable the page falls back to the numbers embedded in the HTML. The badges are rendered by shields.io from the same file, so they show `invalid` until the first deployment.

## Signal journal (`journal.json`)

`journal/` renders the open journal of strategy S1 from `journal.json`: time (UTC), pair, direction of the first 15-minute candle, move to the close after 1 / 4 / 24 hours (absolute, with a direction arrow) with per-window burst flags `burst_1h` / `burst_4h` / `burst_24h`, and status — `pending` until the 4-hour outcome is known, then `real` (accurate: a burst of 8% in 15 minutes or 15% in an hour within 4 hours, either way) or `false` (missed). S1 warns of a sharp move, not of its direction, so colours mark bursts, not the sign of the move. The summary shows all signals, real ones, and false signals per real one over signals with a known outcome. Strategy conditions are not published. The page re-reads the file every hour and when the tab becomes visible; if the file is missing it shows "The journal is updating".

## Adding or editing texts

1. Every visible string lives in `i18n/ru.json` and `i18n/en.json` under the same flat key (`home.hero.title`, `roadmap.p3.1`, …).
2. HTML elements reference keys with `data-i18n`, `data-i18n-html` (for inline markup) or `data-i18n-attr="attr:key"`; the Russian text inside the HTML is the no-JavaScript fallback.
3. Before committing, run the stop-word check from the repository root:

```bash
python -I tools/check_texts.py
```

It scans both dictionaries, this README and all HTML pages and exits with a non-zero code if any public text contains a forbidden word or pattern (promotional claims, dates, personal names and so on).

## Brand

Final logo kit in `assets/brand/` (the editable source file is kept outside the repository):

| File | Use |
|---|---|
| `logo.svg` | main logo: the mark inside a gold ring, transparent background — site header, `/token`, README |
| `logo-512.png` … `logo-32.png` | raster logo in 512 / 256 / 128 / 64 / 32 px |
| `mark.svg`, `mark-1024.png` | the mark alone, without the ring |
| `mark-on-dark.svg` | mark for dark backgrounds |
| `mark-on-light.svg`, `mark-on-light-1024.png` | mark for light backgrounds |
| `favicon.ico`, `apple-touch-icon.png` | browser tab and iOS home-screen icons |
| `avatar-1024.png` | avatar for Telegram, X and GitHub |
| `fatumon-square-1200.png` | square card for posts |
| `og-image.png` | 1200×630 social preview (`og:image`, `twitter:image`) |

The animated green candle on the pages is a separate mascot, not the logo.

## Games page

`games/` presents the Telegram mini app [@fatumon_bot](https://t.me/fatumon_bot). Every "Play" button opens `https://t.me/fatumon_bot?startapp=site`: the game's own analytics records the start parameter `site` as a separate source (Telegram start parameters allow only letters, digits, `_` and `-`, so UTM tags cannot be used). Game names and descriptions are taken from the game's dictionaries without rewording; the art in `assets/games/` is copied from the game's asset folder. The "Rules" link points to the Points section of the Terms (`terms/#game`); the anchor is moved by `app.js` to whichever language block is visible.

## Fonts

All fonts are self-hosted from `assets/fonts/` (latin + cyrillic subsets, woff2) and declared with `@font-face` in `assets/style.css` with `font-display: swap`. No request goes to Google Fonts, so visitors' IP addresses are not shared with a third party for typography.

| Font | Use | License |
|---|---|---|
| Manrope (variable, 400–800) | text and headings | SIL OFL 1.1 |
| JetBrains Mono (variable, 400–600) | tags, numbers, logo | SIL OFL 1.1 |
| Press Start 2P | pixel-display labels | SIL OFL 1.1 |
| VT323 | pixel-display numbers | SIL OFL 1.1 |

License texts: [`assets/fonts/LICENSES.md`](assets/fonts/LICENSES.md).

## Legal pages

`terms/` and `privacy/` hold the Terms of Service and the Privacy Policy (version 0.1, drafts pending legal review). Their texts are long, so they live in the HTML as two language blocks (`data-lang-block="ru|en"`) that the language switcher shows and hides; titles and descriptions use the usual dictionaries.

## Deployment

GitHub Pages serves the `main` branch from the repository root. `CNAME` points the site at the custom domain; `.nojekyll` keeps Pages from touching the files.

## Contact

- Email: [fatumon.token@gmail.com](mailto:fatumon.token@gmail.com)
- Telegram: [t.me/fatumon](https://t.me/fatumon)
- X: [x.com/fatumon_token](https://x.com/fatumon_token)
- GitHub: [github.com/fatumon-token](https://github.com/fatumon-token)

## License

[MIT](LICENSE) © Fatumon
