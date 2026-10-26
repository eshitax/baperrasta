 ┌──────────────────────────────────────────────┐
 │        B A P E R   R A S T A                 │
 │  a full local copy of baperrasta.com         │
 │  repo: https://github.com/eshitax/baperrasta │
 │  open source by: Eshita Jahan                │
 └──────────────────────────────────────────────┘

> a low-poly 3D Bengali driving game — rebuildable, self-hostable,
> deploy anywhere: render / vercel / railway / any VPS.

## WHAT IS THIS
- one python server, zero pip dependencies (stdlib only)
- serves the whole game: html, js, fonts, clips, sounds, scoreboard
- `/api/*` also ships as standalone WSGI handlers for serverless (vercel)

```
 $ tree -L 2 --dirs-first    # the whole app
 .
 ├── index.html             # the game + menu (also 404 fallback)
 ├── about.html             # about / credits / open-source link
 ├── game.*.js              # the 3D game engine (three.js, minified)
 ├── server.py              # the http server (this runs everywhere)
 ├── api/                   # vercel serverless /api/*  (vercel)
 ├── data/board.json       # weekly scoreboard snapshot
 ├── fonts/, clips/, icons/, about/
 ├── Dockerfile            # railway + vps (docker)
 ├── Procfile              # render + railway (procfile)
 └── requirements.txt      # empty — stdlib only
```

## RUN LOCALLY

```bash
python3 server.py            # serves on http://localhost:8080
PORT=8000 python3 server.py  # or pick a port
```

### routes handled by server.py

| route                        | action                                        |
|------------------------------|-----------------------------------------------|
| `/`                          | the game (index.html)                         |
| `/about` → about.html        | about / credits / open-source link            |
| `/privacy` → privacy.html    | privacy policy                                |
| `/disclaimer` → disclaimer.html | disclaimer                                 |
| `GET /api/board`             | proxies live leaderboard, falls back to snapshot |
| `POST /api/run`              | returns a run token (`{t, ok}`)               |
| `POST /api/score`            | ranks your loss against this week's board     |
| `POST /api/name`             | accepts a poster name                         |
| `POST /api/subscribe`        | accepts an email                              |

> all `/api/*` POST endpoints are mocked locally (no backend db),
> but the shape/response matches the real game.

## SETUP / CUSTOMIZATION

### make the pedestrians & riders look real

the game is a single minified JS blob. edits are done as exact-string
replacements (old → new). we already rewrote two functions:

- `o0()` — the pedestrian body builder:
  head with neck, jaw, ears, nose, brows, lips, eyes + skin-tinted
  limbs, thighs/knees/calves/forearms/elbows, fuller hair cap.
- `Vo()` — the rickshaw rider head: fuller skull, ears, nose tip,
  dark eyes, brows, hair cap.

### swap the GitHub link

everywhere the site links the repo it points to
`https://github.com/eshitax/baperrasta` (menu corner button, game-over
footer, about page). change it once in `index.html`, then:

```bash
cp index.html 404.html   # keep the 404 page in sync
```

### rename the credit

menu + game-over credit line says `Open source by Eshita Jahan`.
it appears in `index.html`, `about.html`, `privacy.html`,
`disclaimer.html` — edit all of them, then re-sync `404.html`.

## DEPLOY

four targets, zero config files needed on render/vercel
(they auto-detect), docker/procfile for railway/vps:

### render

```yaml
# pushed to a github repo → render.com: new web service
# build:     (empty)
# start:     python server.py
# env:       PORT (auto-set by render)
```

### vercel

- static files + the `api/*.py` WSGI functions are auto-detected.
- `/api/*` → serverless; everything else → static.
- no build command, no config required.

### railway

```bash
# railway reads the Dockerfile (or Procfile → python3 server.py)
railway init && railway up
```

### vps

```bash
# with docker
docker build -t baper-rasta .
docker run -d --restart always -p 80:8000 baper-rasta

# without docker
python3 server.py

# put it behind nginx/caddy for port 80 + TLS
```

## REPO LAYOUT (DETAIL)

| path              | what it is                                        |
|-------------------|---------------------------------------------------|
| `server.py`       | stdlib ThreadingHTTPServer, route rewrites, mocks |
| `api/_lib.py`     | shared logic for the vercel functions             |
| `api/_wsgi.py`    | tiny WSGI adapter for vercel python runtime       |
| `api/board.py`    | `/api/board` → live board (vercel)                |
| `api/run.py`      | `/api/run` → run token                            |
| `api/score.py`    | `/api/score` → rank + cut                         |
| `api/name.py`     | `/api/name` → accept name                         |
| `api/subscribe.py`| `/api/subscribe` → accept email                   |
| `data/board.json` | weekly leaderboard snapshot (fallback)            |
| `Dockerfile`      | python:3.12-slim, serves on $PORT                 |
| `Procfile`        | `web: python3 server.py`                          |
| `requirements.txt`| empty (no third-party deps)                       |
| `runtime.txt`     | python-3.12.0 (render)                            |
| `start.sh`        | `#!/bin/sh exec python3 server.py`                |
| `.dockerignore`   | keeps build context lean                          |

## SMOKE TEST

```bash
curl -s http://localhost:8080/            # 200, the game
curl -s http://localhost:8080/about       # 200, about page
curl -s http://localhost:8080/api/board   # json leaderboard
curl -sX POST http://localhost:8080/api/run -d '{}'   # {"t": "...", "ok": true}
```

## CREDITS

- game & artwork: **Omar Faruqe Riyad** (baperrasta.com)
- open source packaging: **Eshita Jahan**
- repo: https://github.com/eshitax/baperrasta
