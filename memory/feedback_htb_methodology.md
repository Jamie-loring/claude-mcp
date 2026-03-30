---
name: HTB/CTF engagement methodology
description: Lessons learned from HTB boxes — how to approach enumeration, payload placement, and tooling
type: feedback
---

## Verify constraints before building payloads

Always confirm ownership, permission, and trigger conditions on targets before writing exploit code.

**Why:** On Variatype, spent significant time placing CVE-2024-25081 ZIPs as www-data-owned files. The cron only processed variatype-owned files — a constraint that should have been confirmed first.

**How to apply:** Before building any payload that depends on a cron/process picking it up, verify: who runs the consumer, what file attributes it requires (owner, extension, name pattern), and what directory it watches.

---

## Check file extension trigger conditions for CVEs

When using a CVE that depends on file type detection, confirm the exact extension or magic bytes the vulnerable component requires.

**Why:** CVE-2024-25081 (fontforge ZIP injection) only fires when the outer file has a `.zip` extension. Placing the payload as `.ttf` wasted multiple cron cycles.

**How to apply:** Before deploying a file-based CVE exploit, read the CVE or test the trigger condition with a canary payload (e.g. `id > /tmp/test`) first.

---

## Use SO_REUSEADDR in all custom HTTP servers

Always set `allow_reuse_address = True` (or equivalent) when writing quick exploit HTTP servers.

**Why:** Previous session left port 5555 in TIME_WAIT. The plain `TCPServer` failed to bind, wasting time diagnosing why `ss` showed no listener but Python couldn't bind.

**How to apply:** Boilerplate for all one-off exploit servers: `socketserver.TCPServer.allow_reuse_address = True`.

---

## Timestamp-check artifacts before debugging "broken" exploits

When an exploit appears not to be firing, check the modification timestamps of relevant files before assuming the injection is broken.

**Why:** On Variatype, stale `.ttf` files from a prior session were present in the upload directory. The injection appeared not to be working because the old file wasn't being re-processed — not because the injection was broken.

**How to apply:** When debugging a "not firing" exploit, first verify the target file is current (check mtime), is the right owner, and is actually new to the consumer. Place a canary first.

---

## Never redo completed objectives — always check notes first

At the start of every session, check memory/notes for what's already been accomplished. If user.txt is captured, go straight to root. Never re-exploit a foothold or re-capture a flag you already have.

**Why:** On Variatype, user.txt was already in /tmp/uf_s from a prior cron run but we didn't check before attempting the exploit again. Wasted a cron cycle and added unnecessary noise.

**How to apply:** First thing every session — read the box memory file. If a flag is listed, it's done. Move to the next objective immediately. The order is always: foothold → user.txt → root.txt. Don't revisit a completed step.

---

## Never brute force unless the password is on rockyou.txt

If a password isn't on rockyou.txt, it is not worth brute forcing. No exceptions. Do not guess thematic passwords, mutate usernames, or spray custom wordlists.

**Why:** Thematic guessing and custom wordlists waste time and are almost never the intended path. Real credentials are found through enumeration — config files, env vars, git history, process memory, scripts, logs. The user stated this as an absolute rule.

**How to apply:** If stuck on credentials, enumerate harder first. If brute force is warranted at all, use rockyou.txt and nothing else. If rockyou fails, stop and ask the user rather than expanding the wordlist or guessing.

---

## os.path.join() ignores base when second arg is absolute

`os.path.join('/some/base', '/absolute/path')` returns `/absolute/path` — the base is silently discarded.

**Why:** This was the root of the setuptools PackageIndex path traversal on Variatype. The `..` stripping check doesn't address absolute path injection via percent-decoded URL paths.

**How to apply:** When auditing code that calls `os.path.join(user_controlled_base_or_suffix)`, check for both `..` traversal AND absolute path injection (leading `/` after URL decode). Look for `urllib.parse.unquote()` feeding into `os.path.join()`.
