---
title: Self-hosted E2E chat server on RHEL 10
date: 2026-11-06
tags: [rhel, selinux, firewalld, postgresql, cloudflare]
publish: true
---

# Self-hosted E2E chat server on RHEL 10

## Goal
Replace a third-party messenger (Telegram) with a **self-hosted, end-to-end-encrypted** chat server that my AI assistant and I use to talk. It has to be reachable from anywhere, without opening inbound ports at home.

## Setup
- **Server VM:** RHEL 10.2 on Proxmox, **SELinux enforcing**, minimal install (sshd + Cockpit only).
- **Stack:** the chat app (SuttonChat), **PostgreSQL**, **Valkey** (Redis-compatible), all as systemd services.
- **Exposure:** a public hostname through a **Cloudflare Tunnel** (no port-forward). The bot API port is open in firewalld **only to the assistant VM's IP**.
- **Security:** E2E encryption with a pinned device fingerprint; an admin account with email via Gmail SMTP (587).
- **Access model:** the assistant has an SSH account with **narrow sudo** (only `ss -ltnp` and `firewall-cmd --list-*`).

## What broke and how I fixed it
- *Tunnel path blocking:* the internal-only API path is blocked at the tunnel. It returns 502 instead of a clean 404. It works, but it's noted for cleanup.
- *Code review before install:* I reviewed the bridge/plugin code first. It only talks to the server, reads a transcript tail for token counts, and relays permission prompts to admins.

## What I learned
- Zero-trust exposure (tunnels) beats port-forwarding at home.
- Least-privilege firewall rules: allow-list one source IP per internal port.
- Reviewing third-party code before giving it access.

## Skills used
RHEL 10, SELinux, firewalld, systemd, PostgreSQL, Valkey, Cloudflare Tunnel, SSH hardening, sudoers.
