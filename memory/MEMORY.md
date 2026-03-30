# Claude Memory

## General Working Style

- **CORE RULE**: Always stop and ask the user for help when stuck — CAPTCHAs, missing tooling, unclear paths, anything. Never spin wheels silently. See `feedback_ask_for_help.md`.
- I can install missing tools myself when able, but should ask if something is blocked or unclear.
- **HTB/CTF methodology rules** — See `feedback_htb_methodology.md`:
  - Verify ownership/extension/trigger constraints BEFORE building payloads
  - Always use a canary to confirm exploit triggers before deploying the real payload
  - Use `SO_REUSEADDR` in all custom HTTP servers
  - Check artifact mtimes before assuming an exploit is broken
  - `os.path.join(base, '/abs/path')` discards the base — look for this in path-traversal audits
  - **No thematic password guessing** — enumerate config files, env vars, git history, and scripts first; ask if truly blocked
  - **Never redo completed objectives** — check notes first every session; if user.txt is done, next stop is always root.txt

## Completed HTB: "Variatype" box

See `htb-variatype.md` for full attack chain and flags.

## In Progress: HTB "Pirate" box

See `htb-pirate.md` for full state, creds, and attack chain.

## GitHub API Access

See `reference_github_access.md` — token in `pass show github/pat`, push via Python urllib (curl arg list too long for large files). install.sh lives on the `ShellShock` branch.

## browser-vm container

See `project_browser_vm_creds.md` for VNC + API key credentials.

## Jamie's professional profile & job hunting

See `user_profile.md` — cloud SIEM/security/pentesting/GRC, targeting new role via Ghost on LinkedIn/Dice/Glassdoor.
See `project_job_hunt.md` — scraper rules, hard exclusions (Cyderes, Wells Fargo), trial-run-only mode, human-pace ghost ops.

## Completed CTF: HTB "facts" box

See `htb-facts.md` for full attack chain and flags.
