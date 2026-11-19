import json, time, os, sys

ROOT = os.environ.get("YT_ROOT", r"<repo>")
SRC = os.environ.get("YT_STATE") or r"C:\.playwright-mcp\yt_state.json"
OUT = os.path.join(ROOT, "cookies.txt")

state = json.load(open(SRC, encoding="utf-8"))
cookies = state.get("cookies", [])
lines = [
    "# Netscape HTTP Cookie File",
    "# exported from Chrome profile via Playwright storageState",
    "",
]
now = time.time()
n = 0
for c in cookies:
    domain = c.get("domain", "")
    if not domain:
        continue
    include_sub = domain.startswith(
        "."
    )  # cookiejar asserts initial_dot == domain_specified
    path = c.get("path", "/")
    secure = "TRUE" if c.get("secure") else "FALSE"
    expires = int(c.get("expires", -1))
    # -1 / 0 means session cookie -> write large expiry so yt-dlp keeps it
    exp = expires if expires and expires > now else int(now + 86400 * 30)
    name = c.get("name", "")
    value = c.get("value", "")
    lines.append(
        "\t".join(
            [
                domain,
                "TRUE" if include_sub else "FALSE",
                path,
                secure,
                str(exp),
                name,
                value,
            ]
        )
    )
    n += 1
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
yt = [
    c
    for c in cookies
    if "youtube" in c.get("domain", "") or "google" in c.get("domain", "")
]
print(f"wrote {n} cookies to {OUT} (youtube/google: {len(yt)})")
print("sample yt cookies:", [(c["name"], c["domain"]) for c in yt[:8]])
