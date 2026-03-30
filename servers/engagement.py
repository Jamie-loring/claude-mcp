"""
engagement.py — MCP server exposing engagement directories as resources.

Register: claude mcp add engagement-notes python3 ~/tools/scripts/mcp/engagement.py
"""
from mcp.server.fastmcp import FastMCP
import os, glob

mcp = FastMCP("engagement-notes")
BASE = os.path.expanduser("~/engagements")


@mcp.resource("engagements://list")
def list_engagements() -> str:
    """List all engagement directories."""
    if not os.path.exists(BASE):
        return "No engagements directory found."
    dirs = sorted(d for d in os.listdir(BASE) if os.path.isdir(f"{BASE}/{d}"))
    return "\n".join(dirs) if dirs else "No engagements yet."


@mcp.resource("engagement://{machine}/nmap")
def get_nmap(machine: str) -> str:
    """Read all nmap output files for an engagement."""
    files = glob.glob(f"{BASE}/{machine}/nmap/*.txt") + \
            glob.glob(f"{BASE}/{machine}/nmap/*.nmap")
    if not files:
        return "No nmap output found."
    return "\n\n---\n\n".join(open(f).read() for f in sorted(files))


@mcp.resource("engagement://{machine}/loot")
def get_loot(machine: str) -> str:
    """Read loot files for an engagement."""
    loot_files = glob.glob(f"{BASE}/{machine}/loot/*")
    if not loot_files:
        return "No loot yet."
    parts = []
    for f in sorted(loot_files):
        try:
            parts.append(f"=== {os.path.basename(f)} ===\n" + open(f).read())
        except Exception:
            pass
    return "\n\n".join(parts)


@mcp.tool()
def create_engagement(machine: str) -> str:
    """Create a new engagement directory structure (nmap, loot, exploit, www)."""
    for sub in ["nmap", "loot", "exploit", "www"]:
        os.makedirs(f"{BASE}/{machine}/{sub}", exist_ok=True)
    return f"Created: {BASE}/{machine}/"


@mcp.tool()
def store_cred(machine: str, entry: str) -> str:
    """Append a credential line to the engagement loot file."""
    path = f"{BASE}/{machine}/loot/creds.txt"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(entry + "\n")
    return f"Stored in {path}"


if __name__ == "__main__":
    mcp.run()
