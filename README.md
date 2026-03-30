# claude-mcp

Reference repo for building and running [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers with Claude Code.

MCP is Anthropic's open standard for connecting AI models to external tools, resources, and services. Claude Code supports MCP natively — registered servers appear as first-class tools in every session.

---

## Quick Setup

### Install the Python SDK

```bash
pip3 install mcp
# or — already included in ShellShock bootstrap
```

### Register a server with Claude Code

```bash
claude mcp add my-server python3 /path/to/server.py
claude mcp list
```

Or edit `~/.claude/settings.json` directly:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python3",
      "args": ["/path/to/server.py"],
      "env": {
        "SOME_VAR": "value"
      }
    }
  }
}
```

---

## Transports

| Transport | When to use |
|-----------|------------|
| `stdio` | Local servers — Claude Code spawns them as subprocesses (default) |
| `SSE` | Remote services over HTTP — useful for shared/networked tools |

---

## Example Servers

### Pentest Tools Wrapper

Wraps common tools with structured output Claude can reason over.

```python
# servers/pentest.py
from mcp.server.fastmcp import FastMCP
import subprocess, shlex

mcp = FastMCP("pentest-tools")

@mcp.tool()
def nmap_scan(target: str, flags: str = "-sV --top-ports 1000") -> str:
    """
    Run nmap against an authorised target.
    Always confirm scope before calling.
    """
    cmd = ["nmap"] + shlex.split(flags) + [target]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return result.stdout or result.stderr

@mcp.tool()
def ffuf_fuzz(url: str, wordlist: str = "~/wordlists/common-dirs.txt",
              extensions: str = "") -> str:
    """Directory/file fuzzing with ffuf. URL must contain FUZZ placeholder."""
    import os
    wl = os.path.expanduser(wordlist)
    cmd = ["ffuf", "-u", url, "-w", wl, "-mc", "200,204,301,302,307,401,403"]
    if extensions:
        cmd += ["-e", extensions]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout

@mcp.tool()
def engagement_note(machine: str, note: str = "") -> str:
    """Read or append to an engagement's notes file."""
    import os
    path = os.path.expanduser(f"~/engagements/{machine}/notes.md")
    if note:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            f.write(f"\n{note}\n")
        return f"Appended to {path}"
    elif os.path.exists(path):
        return open(path).read()
    return "No notes yet."

@mcp.resource("engagement://{machine}/loot")
def get_loot(machine: str) -> str:
    """Read the loot file for an engagement."""
    import os
    path = os.path.expanduser(f"~/engagements/{machine}/loot/creds.txt")
    return open(path).read() if os.path.exists(path) else "Empty."

if __name__ == "__main__":
    mcp.run()
```

Register:
```bash
claude mcp add pentest-tools python3 ~/tools/scripts/mcp/pentest.py
```

---

### Engagement Note Server

Lightweight resource server exposing engagement directories.

```python
# servers/engagement.py
from mcp.server.fastmcp import FastMCP
import os, glob

mcp = FastMCP("engagement-notes")
BASE = os.path.expanduser("~/engagements")

@mcp.resource("engagements://list")
def list_engagements() -> str:
    dirs = [d for d in os.listdir(BASE) if os.path.isdir(f"{BASE}/{d}")]
    return "\n".join(sorted(dirs))

@mcp.resource("engagement://{machine}/nmap")
def get_nmap(machine: str) -> str:
    files = glob.glob(f"{BASE}/{machine}/nmap/*.txt") + \
            glob.glob(f"{BASE}/{machine}/nmap/*.nmap")
    return "\n\n---\n\n".join(open(f).read() for f in files) if files else "No nmap output."

@mcp.tool()
def create_engagement(machine: str) -> str:
    """Create a new engagement directory structure."""
    for sub in ["nmap", "loot", "exploit", "www"]:
        os.makedirs(f"{BASE}/{machine}/{sub}", exist_ok=True)
    return f"Created: {BASE}/{machine}/"

if __name__ == "__main__":
    mcp.run()
```

---

### Shell Gateway (controlled)

Controlled shell execution with basic guardrails.

```python
# servers/shell.py
from mcp.server.fastmcp import FastMCP
import subprocess, shlex

mcp = FastMCP("shell-gateway")

BLOCKED = ["rm -rf /", "dd if=", "> /dev/sd", "mkfs"]

@mcp.tool()
def run(command: str, timeout: int = 30) -> str:
    """
    Execute a shell command. Returns stdout + stderr.
    Blocked patterns: rm -rf /, dd if=, raw disk writes.
    """
    for pattern in BLOCKED:
        if pattern in command:
            return f"BLOCKED: command contains disallowed pattern '{pattern}'"
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=timeout
    )
    output = result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    return output or "(no output)"

if __name__ == "__main__":
    mcp.run()
```

---

## Claude Code Configuration Reference

### ~/.claude/settings.json

```json
{
  "autoApproveTools": ["bash"],
  "skipDangerousModePermissionPrompt": true,
  "mcpServers": {
    "pentest-tools": {
      "command": "python3",
      "args": ["/home/user/tools/scripts/mcp/pentest.py"]
    },
    "engagement-notes": {
      "command": "python3",
      "args": ["/home/user/tools/scripts/mcp/engagement.py"]
    }
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "INPUT=$(cat); CMD=$(echo \"$INPUT\" | jq -r '.tool_input.command // empty'); if echo \"$CMD\" | grep -qFe 'pattern-to-block'; then echo '{\"continue\":false,\"stopReason\":\"Blocked — reason\"}'  ; fi"
        }]
      }
    ]
  }
}
```

### CLAUDE.md (project-level instructions)

Drop in any project directory. Claude Code reads it as standing instructions:

```markdown
# Project — Claude Code Standing Instructions

## Autonomy
[What Claude can do without asking]

## Constraints
[Hard limits — never cross these]

## Context
[Domain knowledge, architecture notes, important paths]

## Operating Philosophy
[How to approach the work]
```

Claude Code checks every directory from the working dir up to `~/` for CLAUDE.md files. They stack — parent rules apply unless overridden by a child.

### Persistent Memory

```
~/.claude/projects/<working-dir-hash>/memory/
├── MEMORY.md           — session index (loaded automatically)
├── user_profile.md     — who the user is, preferences
├── feedback_*.md       — corrections and validated approaches
├── project_*.md        — active project state
└── reference_*.md      — pointers to external systems
```

Types: `user`, `feedback`, `project`, `reference`. Each has frontmatter (`name`, `description`, `type`) and content structured as: fact/rule → **Why:** → **How to apply:**.

---

## Tips

* **Start simple** — `FastMCP` is the easiest entry point; move to low-level `Server` only if you need streaming or advanced lifecycle control
* **Scope tools tightly** — narrow docstrings help Claude pick the right tool
* **Resources vs Tools** — use resources for data Claude reads, tools for actions Claude takes
* **stdio is the default** — for local servers, just `mcp.run()` with no arguments
* **Restart Claude Code** after adding/changing MCP servers in settings.json

---

**Author:** Jamie Loring
