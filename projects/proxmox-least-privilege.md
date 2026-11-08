# Least-privilege Proxmox API access (dev vs prod)

## Goal
Give an automation account (my AI assistant) access to two Proxmox VE 9 nodes, with **full rights on dev but read-mostly on prod**.

## Setup
- A dedicated PVE user with one **API token per node**. Token secrets live in 0600 files, never in chat or notes.
- **Dev node:** `PVEAdmin` role. It may act on its own but must report what it does.
- **Prod node:** `PVEAuditor` + `PVEVMUser` on `/vms`. Any change needs a **state snapshot first and my explicit approval**.
- Guest SSH: separate keys for dev and prod VMs. Full sudo on dev; narrow sudo on prod.

## What broke and how I fixed it
- **401 on both tokens:** the token ID needs the right realm and case (`User@pam!token`). Fixed by checking the exact token ID.
- **Prod token authenticated but saw nothing:** with *privilege separation* on, a token's permissions are its **own ACL**, intersected with the user's. Turning privsep off (or adding ACLs to the token itself) fixed it.

## What I learned
- How PVE API tokens and privilege separation interact.
- Separate dev and prod blast radius: different keys, roles and approval rules.

## Skills used
Proxmox VE 9, RBAC/ACLs, REST API (curl), SSH key management, change-control process.
