# Nightly LAN device monitoring

## Goal
Get a message whenever a **new device** joins the home network, without installing a full NMS and without intrusive scanning.

## How it works ([script](lanwatch.sh.txt))
1. A cron job at 02:47 sends **one ping to each address** in the /24. That populates the ARP table, even for hosts that drop ICMP (they still answer ARP).
2. Read `ip neigh` and collect the **MAC → IP** pairs.
3. Compare against `known.tsv` (a baseline of 11 devices). Look up each new MAC's **vendor (OUI)** from `/usr/share/hwdata/oui.txt`.
4. Send new devices as an alert to my chat server's bot API, and add them to the baseline.

## Findings from the first sweep
- It identified every device by vendor OUI: Cisco Meraki gear, Proxmox guests (`BC:24:11`), an HP host, a desktop that ignores ping, and a few IoT devices.
- A host that drops ping is **still visible at Layer 2**. That's a good CCNA reminder that ARP lives below IP filtering.

## What I learned
- ARP/neighbor tables and OUIs for inventory.
- A first parsing bug: the field positions in `ip neigh` output change when you pass `dev`, so I made it parse by keyword.

## Skills used
Bash, ARP, IP neighbor tables, MAC OUI lookup, cron, REST alerting.
