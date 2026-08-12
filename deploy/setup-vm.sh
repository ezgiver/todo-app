#!/usr/bin/env bash
# deploy/setup-vm.sh — One-time VM setup script for Ubuntu 22.04+ (ARM/x86).
# Run this ONCE after SSH-ing into a fresh Oracle Cloud VM.
#
# Usage: bash deploy/setup-vm.sh
#
set -euo pipefail

echo "==> Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

echo ""
echo "==> Installing Docker..."
# Remove old versions if any
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install prerequisites
sudo apt-get install -y \
  ca-certificates \
  curl \
  gnupg \
  lsb-release

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repo
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow running docker without sudo
sudo usermod -aG docker "$USER"

echo ""
echo "==> Opening firewall ports (80, 443)..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save

echo ""
echo "==> Installing git (if not present)..."
sudo apt-get install -y git

echo ""
echo "============================================"
echo "  VM setup complete!"
echo "============================================"
echo ""
echo "IMPORTANT: Log out and back in for docker group to take effect:"
echo "  exit"
echo "  ssh todo-vm"
echo ""
echo "Then clone your repo and deploy:"
echo "  git clone https://github.com/ezgiver/todo-app.git ~/todo-app"
echo "  cd ~/todo-app"
echo "  cp deploy/.env.example deploy/.env"
echo "  nano deploy/.env   # fill in DATABASE_URL, SECRET_KEY, DOMAIN"
echo "  bash deploy/deploy.sh"
