# Fly.io Deployment Guide

Deploy the todo app to **Fly.io** — free, automatic HTTPS, no credit card needed.

---

## Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────┐
│  Fly.io (HTTPS automatic)       │
│                                 │
│  ┌──────────────────────────┐   │
│  │  Single container        │   │
│  │  gunicorn :8080          │   │
│  │  ├── /api/*  → Flask     │   │
│  │  └── /*      → React SPA │   │
│  └──────────────────────────┘   │
└──────────────────┬──────────────┘
                   │
                   ▼
        ┌──────────────────┐
        │  Neon PostgreSQL  │
        │  (external DB)    │
        └──────────────────┘
```

One container handles everything — Flask serves both the API and the built
React frontend. Fly.io handles HTTPS automatically.

---

## Prerequisites

- A [Neon](https://console.neon.tech) PostgreSQL database (already migrated)
- [Homebrew](https://brew.sh) installed on your Mac

---

## Step 1: Install the Fly CLI and sign up

```bash
brew install flyctl
```

Sign up using your GitHub account (no credit card needed):

```bash
fly auth signup
```

This opens a browser window — click "Continue with GitHub", authorize, done.

If you already have an account:

```bash
fly auth login
```

---

## Step 2: Pick your app name and region

Open `fly.toml` in the project root and update these two lines:

```toml
app = "todo-app-ezgiver"   # must be globally unique on Fly.io
primary_region = "ams"     # pick your nearest region
```

**Nearest regions:**

| Your location | Code |
|---|---|
| Western Europe | `ams` (Amsterdam) or `fra` (Frankfurt) |
| US East | `iad` (Virginia) |
| US West | `sjc` (San Jose) |
| Asia Pacific | `sin` (Singapore) |

Full list: https://fly.io/docs/reference/regions/

> **App name tip:** It becomes part of your URL: `https://your-app-name.fly.dev`
> If the name is taken, Fly.io will tell you during the next step.

---

## Step 3: Register the app on Fly.io

Run this from the **project root** (where `fly.toml` lives):

```bash
fly launch --no-deploy
```

When prompted:
- **"Would you like to copy its configuration to the new app?"** → type `y`
- **"Would you like to set up a Postgresql database?"** → type `n` (using Neon)
- **"Would you like to set up an Upstash Redis database?"** → type `n`

This registers the app name on Fly.io without deploying anything yet.

---

## Step 4: Set your secrets

Secrets are encrypted environment variables — never visible in logs or code:

```bash
# Your Neon connection string (copy from https://console.neon.tech → Connection Details):
fly secrets set DATABASE_URL="postgresql://user:password@ep-xxxx.us-east-2.aws.neon.tech/todo_db?sslmode=require"

# Generate and set a Flask secret key in one command:
fly secrets set SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

> ⚠️ Always wrap `DATABASE_URL` in double quotes — the connection string contains
> special characters that the shell would misread without them.

Verify they were saved:
```bash
fly secrets list
# NAME          DIGEST    CREATED AT
# DATABASE_URL  xxxxxxxx  just now
# SECRET_KEY    xxxxxxxx  just now
```

---

## Step 5: Deploy

```bash
fly deploy
```

What happens:
1. Fly.io builds the Docker image on their servers (React frontend + Flask backend)
2. Pushes the image to their registry
3. Starts the container and runs health checks against `/api/health`
4. Prints your live URL when done

First deploy takes ~3 minutes. Subsequent deploys are faster (layers are cached).

**Expected output at the end:**
```
Visit your newly deployed app at https://todo-app-yourname.fly.dev/
```

---

## Step 6: Verify

```bash
# Check the app is alive:
fly open
# Opens https://todo-app-yourname.fly.dev in your browser

# Check the API directly:
curl https://todo-app-yourname.fly.dev/api/health
# {"status": "ok"}

# View live logs:
fly logs
```

---

## Step 7: Verify data persistence

Test that todos survive a redeploy (data lives in Neon, not the container):

```bash
# 1. Open the app, create a todo
fly open

# 2. Redeploy
fly deploy

# 3. Open again — your todo should still be there
fly open
```

---

## Redeploying after code changes

Every time you push new code and want it live:

```bash
fly deploy
```

That's it. Fly.io builds, deploys, and switches traffic with zero downtime.

---

## Common operations

```bash
fly logs              # Live log stream
fly status            # Container health and region info
fly ssh console       # SSH into the running container
fly secrets list      # List secret names (values are never shown)
fly secrets set KEY="value"   # Add or update a secret
fly open              # Open the app in your browser
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `app name already taken` | Change `app` in `fly.toml` to a unique name |
| `SECRET_KEY is not set. Refusing to start` | Run `fly secrets set SECRET_KEY="..."` |
| `DATABASE_URL not set` / DB connection error | Run `fly secrets set DATABASE_URL="..."` — check Neon is not suspended |
| Deploy fails at health check | Run `fly logs` immediately after to see the crash reason |
| App loads but `/api/*` returns 500 | Run `fly logs \| grep ERROR` |
| `fly launch` says app already exists | You already registered it — just run `fly deploy` |
