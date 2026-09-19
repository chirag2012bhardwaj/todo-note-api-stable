# Todo + Notes App

A small full-stack app (Flask + SQLite + vanilla JS) combining a to-do list with due-time alarms
and a pinnable notes board. Built from scratch as a Day 1 "packaging" project — the goal was to
containerize a real app properly, not just wrap something pre-made.

## Run it

Pull and run the pre-built image straight from Docker Hub:

```bash
docker compose up -d
```

App will be available at `http://localhost:5000`. Data persists across restarts via a named
Docker volume.

To build from source instead:

```bash
docker build -t todo-notes-app .
docker run -d -p 5000:5000 -v todo-notes-data:/app todo-notes-app
```

## Features

- Create, complete, and delete todos with an optional due time
- Browser alert fires when a todo's due time passes (checked every 15s while the tab is open)
- Create, pin, and delete notes — pinned notes stay at the top
- Dark mode UI, pastel accents
- SQLite persistence via a Docker named volume

## Docker image

Published at [`chirag2012/todo-notes-app`](https://hub.docker.com/r/chirag2012/todo-notes-app) on Docker Hub.

**Image size**: ~49MB (local) / ~47MB (Docker Hub compressed), down from the ~1GB `python:3.12`
base image. Achieved via:
- Multi-stage build — dependencies are installed in a disposable `builder` stage; only the
  final `/opt/venv` is copied into the runtime image, leaving pip, build tools, and caches behind
- `python:3.12-slim` base instead of the full image
- `.dockerignore` excluding `venv/`, `__pycache__/`, and local `.db` files from the build context

## Security/production practices

- Runs as a dedicated non-root user (`appuser`), not root
- Served via Gunicorn (production WSGI server), not Flask's dev server
- `HEALTHCHECK` instruction polls `/todos` every 30s so container orchestrators can detect failures
- Parameterized SQL queries throughout (no string-formatted queries, avoids SQL injection)

## What I learned

The most useful bug I hit: the app worked fine locally with `python app.py`, but crashed with
`sqlite3.OperationalError: no such table: todos` once containerized with Gunicorn. The cause —
`init_db()` was only called inside `if __name__ == "__main__":`, which never runs when Gunicorn
imports the app as a module (`app:app`) instead of executing the file directly. Fixed by moving
the call to run unconditionally at import time. A good reminder that "works with the dev server"
and "works in production" aren't the same claim.

## Tech stack

Flask, SQLite, Gunicorn, vanilla JS/HTML/CSS, Docker (multi-stage build)
