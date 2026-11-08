# GNOME black screen after a partial RHEL update

## Goal
Get the desktop working again on a RHEL 10 VM: after login, GDM showed only a black screen.

## Diagnosis
- `gnome-shell` 49 (el10_2) was crashing on start. The log showed a **missing GSettings schema**: `org.gnome.desktop.screen-time-limits`.
- `rpm -q` showed `gsettings-desktop-schemas` and `glib2` still on **el10_0** builds, while gnome-shell was el10_2. A **partial update** had left the packages mismatched.

## Fix
- Plan: a full `dnf upgrade` (193 packages pending) plus a reboot, to bring everything to the same minor release.
- The full upgrade ran, followed by a reboot, and GNOME worked again.
- Verified: `gdm` active, `gnome-shell` running for the greeter, then for my user session after login.

## What I learned
- On RHEL, desktop components must be on the same minor release. Never half-update.
- Read the shell's own error (missing schema) instead of reinstalling blindly.

## Skills used
RHEL 10, dnf, rpm, systemd/journal, GNOME/GDM, GSettings.
