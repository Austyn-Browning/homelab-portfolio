# Real Let's Encrypt certs for every lab GUI

## Goal
Stop clicking through "not secure" warnings on the six web GUIs in the lab, and get trusted certs that renew on their own, without opening anything to the internet.

| GUI | Name | Method |
|---|---|---|
| Proxmox prod | pve-prod.lab.example.com:8006 | PVE built-in ACME |
| Proxmox dev | pve-dev.lab.example.com:8006 | PVE built-in ACME |
| Proxmox Backup Server | pbs.lab.example.com:8007 | `proxmox-backup-manager acme` |
| Cockpit on 3 RHEL VMs | <host>.lab.example.com:9090 | certbot on one VM, cert pushed |

All certs are valid until 2027-02-05 and renew automatically.

## Setup
- **DNS-01 challenge through Cloudflare**, so nothing needs to be reachable from the internet. The API token is scoped to DNS Edit + Zone Read on one zone, with an IP filter for the lab's public IP, and it is stored in Bitwarden Secrets Manager.
- **Names:** `*.lab.example.com` are Cloudflare *DNS-only* A records pointing at private RFC 1918 addresses.
- **Proxmox / PBS:** built-in ACME account (Let's Encrypt v2) plus the Cloudflare DNS plugin (`CF_Token` + `CF_Zone_ID`). Renewal is handled by the products' own daily jobs.
- **Cockpit:**
  - certbot + certbot-dns-cloudflare run in a user venv on one VM, with no root.
  - At run time the token is written to a tmpfs file and deleted afterwards.
  - Each target has a tiny root helper, `/usr/local/sbin/cockpit-cert-install`. It takes no arguments, reads cert+key from stdin, refuses anything that isn't `*.lab.example.com` or whose key doesn't match, then installs the files and restarts Cockpit.
  - sudoers allows only that helper with no arguments.
  - A daily cron runs `certbot renew` with a deploy hook that pushes renewed certs, and alerts to chat on failure.
- **PBS link:** both PVE nodes were switched from "IP + pinned fingerprint" to `server=pbs.lab.example.com` with no fingerprint, so certificate renewals can't break backups.

## What broke and how I fixed it
- **DNS answers for private IPs vanished.**
  - Cause: the Meraki's DNS forwarder (upstream AT&T) stripped private-IP answers (DNS rebinding protection).
  - Fix: point DHCP DNS at 1.1.1.1/1.0.0.1.
  - Side effect: the MX then stopped answering DNS at all, which broke every box hard-set to the MX for DNS (chat server mail/push, a Proxmox node, the remote-access connector). Fixed each static box.
  - **Lesson:** before a DNS change, list every host with static DNS.
- **Dev node ACME order said "invalid domain".** `CF_Token` held the 32-char *token ID* instead of the token secret. I set the right value through the API.
- **PBS ACME CLI:**
  - Account registration asks two questions (TOS, then EAB). `yes |` answered both wrong; `printf "y\nn\n"` works.
  - `plugin add --data` takes a **file path**. Passing the content made the error message echo the token, so the token was rolled.
  - **Lesson:** read `--help` first, and test with a fake value before using a real secret.
- **`acme cert order` said "not renewing".** It needs `--force true` when a cert already exists.
- **Changing a PVE PBS storage's `server` failed.** It's a fixed parameter: edit `/etc/pve/storage.cfg` or re-create the storage.
- **Cockpit install failed with "invalid group cockpit-ws".** RHEL 10 has no such group, so the files are owned root:root.
- **Prod node ACME account registration failed.** Proxmox requires root@pam for ACME accounts, whatever the role. Root made the account; the rest (plugin, domain, order) only needs Sys.Modify.
- **A permission given to an API token did nothing.** The token had privilege separation off, so it uses its user's permissions and ignores its own. The fix was to put the permission on the user.

## What I learned
- DNS-01 + DNS-only records give public CA certs to private-only services.
- Pinned fingerprints and auto-renewing certs don't mix; use names.
- Least privilege works: narrow API token, a no-arguments sudo helper, temporary roles removed after use.
- "Fast is slow and slow is fast": most of the problems came from rushing a step.

## Skills used
Proxmox VE/PBS API and ACME, Let's Encrypt/certbot, Cloudflare API and DNS, TLS/x509 with openssl, sudoers hardening, bash, cron, DNS troubleshooting, change control (snapshot → approve → verify → rollback plan).
