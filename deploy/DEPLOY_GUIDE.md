# Oracle Cloud VM Deployment Guide

This guide walks you through deploying the todo app to an **Oracle Cloud Always Free** ARM instance with automatic HTTPS via Caddy.

---

## Architecture Overview

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────┐
│  Oracle Cloud VM (Ubuntu ARM)                   │
│                                                 │
│  ┌───────────┐   ┌───────────┐   ┌──────────┐  │
│  │   Caddy   │──▶│  Frontend │   │ Backend  │  │
│  │  :80/:443 │   │  (nginx)  │   │(gunicorn)│  │
│  │           │──▶│  :80      │   │  :5001   │  │
│  └───────────┘   └───────────┘   └────┬─────┘  │
│                                        │        │
└────────────────────────────────────────┼────────┘
                                         │
                                         ▼
                              ┌──────────────────┐
                              │  Neon PostgreSQL  │
                              │  (external DB)    │
                              └──────────────────┘
```

**How traffic flows:**
1. Caddy receives all HTTP/HTTPS traffic on ports 80 and 443
2. Requests to `/api/*` are proxied to the Flask backend (gunicorn on port 5001)
3. All other requests go to the React frontend (nginx serving static files)
4. The backend connects to your Neon PostgreSQL database over the internet

---

## Step 1: Create an Oracle Cloud Always Free VM

### 1.1 Sign up for Oracle Cloud

1. Go to [cloud.oracle.com](https://cloud.oracle.com) and create a free account
2. You'll need a credit card for verification, but **you won't be charged** for Always Free resources
3. Choose your "Home Region" — pick one close to you (this can't be changed later)

### 1.2 Create the VM Instance

1. In the Oracle Cloud Console, go to **Compute → Instances → Create Instance**
2. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `todo-app-vm` |
| **Image** | Ubuntu 22.04 (or 24.04) — Canonical |
| **Shape** | VM.Standard.A1.Flex (ARM) |
| **OCPUs** | 1 (free tier allows up to 4) |
| **Memory** | 6 GB (free tier allows up to 24 GB) |
| **Boot volume** | 50 GB (default, free) |

3. **Networking:**
   - Create a new VCN or use the default
   - Ensure "Assign a public IPv4 address" is checked
   - Select or create a subnet

4. **SSH Keys:**
   - Select "Generate a key pair" and **download both keys**, OR
   - Select "Upload public key" and paste your existing `~/.ssh/id_rsa.pub` (recommended)

5. Click **Create** — the instance will be ready in ~60 seconds

### 1.3 Note your public IP

Once the instance shows "Running," copy the **Public IP address** from the instance details page. You'll use this for SSH and (optionally) direct browser access.

### 1.4 Configure Security Lists (Firewall)

Oracle Cloud blocks ports 80/443 by default. You must open them:

1. Go to **Networking → Virtual Cloud Networks → [your VCN]**
2. Click on your **Subnet → Security List**
3. Click **Add Ingress Rules** and add:

| Source CIDR | Protocol | Dest Port | Description |
|-------------|----------|-----------|-------------|
| `0.0.0.0/0` | TCP | 80 | HTTP |
| `0.0.0.0/0` | TCP | 443 | HTTPS |

> **Why two firewalls?** Oracle Cloud has a VCN-level firewall (Security Lists) AND an OS-level firewall (iptables). You need to open ports in both. The `setup-vm.sh` script handles iptables for you.

---

## Step 2: SSH into the VM

```bash
# If you downloaded Oracle's generated key:
chmod 400 ~/Downloads/ssh-key-*.key
ssh -i ~/Downloads/ssh-key-*.key ubuntu@<YOUR_VM_IP>

# If you used your own key:
ssh ubuntu@<YOUR_VM_IP>
```

**Pro tip:** Add this to `~/.ssh/config` for easy access:

```
Host todo-vm
    HostName <YOUR_VM_IP>
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
```

Then just: `ssh todo-vm`

---

## Step 3: Set Up the VM

Run the setup script (installs Docker, opens firewall ports):

```bash
# On the VM:
git clone https://github.com/ezgiver/todo-app.git ~/todo-app
cd ~/todo-app
bash deploy/setup-vm.sh
```

**Then log out and back in** (so Docker group permissions take effect):

```bash
exit
ssh todo-vm
```

Verify Docker works:
```bash
docker run --rm hello-world
```

---

## Step 4: Configure Environment

```bash
cd ~/todo-app
cp deploy/.env.example deploy/.env
nano deploy/.env
```

Fill in your real values:

```env
DATABASE_URL=postgresql://user:password@ep-xxxx.us-east-2.aws.neon.tech/todo_db?sslmode=require
SECRET_KEY=<your-generated-secret>
DOMAIN=:80
```

> **Generate a SECRET_KEY:**
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## Step 5: Deploy!

```bash
cd ~/todo-app
bash deploy/deploy.sh
```

This will:
1. Pull the latest code from git
2. Build the Docker containers
3. Start everything in detached mode
4. Run a health check on the backend

**Test it:**
```bash
# From your local machine:
curl http://<YOUR_VM_IP>/api/health
# Should return: {"status": "ok"} or similar

# Open in browser:
open http://<YOUR_VM_IP>
```

---

## Step 6: Domain Name + HTTPS (Recommended)

### Should I get a domain?

| Approach | Pros | Cons |
|----------|------|------|
| **IP only** | Free, immediate | No HTTPS, hard to remember, changes if VM recreated |
| **Domain** ($10-15/year) | HTTPS automatic, professional, stable | Small yearly cost |

**Recommendation:** Get a cheap domain from Namecheap, Porkbun, or Cloudflare (~$10/year for a `.dev` or `.app` domain). HTTPS is important for secure cookies (which your Flask session auth uses).

### Set up DNS

1. Buy a domain (e.g., `todo.yourdomain.com`)
2. In your DNS provider, add an **A record**:
   - Name: `todo` (or `@` for root)
   - Value: `<YOUR_VM_IP>`
   - TTL: 300 (5 minutes for testing)

3. Wait for DNS propagation (usually 1-5 minutes)

### Enable HTTPS

Update `deploy/.env`:

```env
DOMAIN=todo.yourdomain.com
```

Restart:
```bash
cd ~/todo-app
docker compose -f docker-compose.prod.yml --env-file deploy/.env down
bash deploy/deploy.sh
```

Caddy will **automatically** obtain a Let's Encrypt certificate. No extra configuration needed!

---

## Step 7: Verify Persistence

Test that data survives redeployments:

```bash
# 1. Create a todo
curl -X POST http://<YOUR_DOMAIN>/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test persistence"}'

# 2. Redeploy
bash deploy/deploy.sh

# 3. Check the todo still exists
curl http://<YOUR_DOMAIN>/api/todos
# Should still show "Test persistence"
```

Data persists because the database is on **Neon** (external), not inside the containers.

---

## Common Operations

### View logs
```bash
cd ~/todo-app
docker compose -f docker-compose.prod.yml --env-file deploy/.env logs -f
docker compose -f docker-compose.prod.yml --env-file deploy/.env logs backend  # just backend
```

### Restart a single service
```bash
docker compose -f docker-compose.prod.yml --env-file deploy/.env restart backend
```

### Full redeploy from local machine
```bash
ssh todo-vm 'cd ~/todo-app && bash deploy/deploy.sh'
```

### Stop everything
```bash
docker compose -f docker-compose.prod.yml --env-file deploy/.env down
```

### Check resource usage
```bash
docker stats
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't reach VM on port 80 | Check Oracle Cloud Security List AND iptables (run `setup-vm.sh` again) |
| Caddy won't get HTTPS cert | Ensure DNS A record points to your VM IP; ensure port 80 is reachable (Let's Encrypt uses HTTP challenge) |
| Backend unhealthy | Check logs: `docker compose -f docker-compose.prod.yml logs backend` |
| Database connection refused | Verify `DATABASE_URL` in `deploy/.env`; ensure Neon project isn't suspended |
| "Permission denied" on Docker | Log out and back in after running `setup-vm.sh` (docker group) |
| ARM image build fails | Both Python and Node base images support ARM natively — this shouldn't happen. If a dependency doesn't support ARM, pin an x86 version |

---

## Cost Summary

| Resource | Monthly Cost |
|----------|-------------|
| Oracle Cloud VM (A1.Flex, 1 OCPU, 6GB RAM) | **Free forever** |
| Neon PostgreSQL (free tier) | **Free** (0.5 GB storage) |
| Domain name | ~$1/month ($10-15/year) |
| **Total** | **~$0-1/month** |

---

## Local Testing (Before Deploying to Oracle Cloud)

You can validate the entire production stack on your local machine before touching the VM.

### Quick test (automated)

```bash
bash deploy/test-local.sh
```

This script will:
1. Build all containers (backend with gunicorn, frontend with nginx, Caddy, local Postgres)
2. Wait for health checks to pass
3. Run 7 smoke tests (API health, frontend serving, todo CRUD, security headers)
4. Tear everything down automatically

### Manual test

```bash
# Start the production-like stack
docker compose -f docker-compose.test-prod.yml up --build

# In another terminal, verify:
curl http://localhost/api/health        # Backend OK?
curl http://localhost                    # Frontend loads?
curl -X POST http://localhost/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "local test"}'          # Create works?

# Teardown
docker compose -f docker-compose.test-prod.yml down -v
```

### What this tests

| Layer | What's validated |
|-------|-----------------|
| Backend Dockerfile | gunicorn starts, serves `/api/health` |
| Frontend Dockerfile | Vite builds, nginx serves SPA |
| Caddy reverse proxy | Routes `/api/*` to backend, `/` to frontend |
| Docker networking | Containers can talk to each other by service name |
| Health checks | Docker waits for backend before starting frontend |

> **Note:** The only thing NOT tested locally is the Neon connection and HTTPS certificates (those require a real domain + public IP). But if the local test passes, the prod deploy will work — just swap the DATABASE_URL.

---

## File Structure (new files)

```
deploy/
├── .env.example     # Template for environment variables
├── Caddyfile        # Caddy reverse proxy configuration
├── deploy.sh        # Deployment script (run on VM)
├── setup-vm.sh      # One-time VM setup script
└── test-local.sh    # Local smoke test (runs full stack, validates, tears down)
docker-compose.prod.yml        # Production compose (no local DB)
docker-compose.test-prod.yml   # Local testing compose (includes local Postgres)
.gitignore                     # Prevents .env from being committed
```
