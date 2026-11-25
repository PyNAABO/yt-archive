"""Download every playlist of the account into raw/ (yt-dlp JSON dumps).

Run first; finalize_export.py then builds the canonical one-file-per-category export.
Cookies are NOT kept: regenerate with state2cookies.py, then delete cookies.txt.
"""

import json, os, re, subprocess, sys, time
from pathlib import Path

# playlist titles contain Malayalam/Arabic; cp1252 consoles raise without this
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.environ.get("YT_ROOT") or str(Path(__file__).resolve().parent.parent)
COOKIES = os.path.join(ROOT, "cookies.txt")
RAW = os.path.join(ROOT, "raw")
STATE = os.environ.get("YT_STATE") or r"C:\.playwright-mcp\yt_state.json"
os.makedirs(RAW, exist_ok=True)


def discover():
    """Fresh account: read the playlist ids off /feed/playlists, there is no playlists.json yet."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(storage_state=STATE, locale="en-US").new_page()
        page.goto(
            "https://www.youtube.com/feed/playlists",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(3000)
        last = 0
        for _ in range(40):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(900)
            n = page.eval_on_selector_all('a[href*="list="]', "els => els.length")
            if n == last:
                break
            last = n
        hrefs = page.eval_on_selector_all(
            'a[href*="list="]', "els => els.map(e => e.getAttribute('href'))"
        )
        browser.close()

    ids = []
    for h in hrefs:
        m = re.search(r"[?&]list=([A-Za-z0-9_-]+)", h or "")
        # WL is always fetched first; LL (liked) is no longer tracked; RD* are generated radios
        if (
            m
            and m.group(1) not in ("WL", "LL")
            and not m.group(1).startswith("RD")
            and m.group(1) not in ids
        ):
            ids.append(m.group(1))
    print(f"discovered {len(ids)} playlists on /feed/playlists")
    return ids


index_path = os.path.join(ROOT, "playlists.json")
if os.path.exists(index_path):
    index = json.load(open(index_path, encoding="utf-8"))
    ids = ["WL"] + [p["playlist_id"] for p in index["playlists"]]
else:
    ids = ["WL"] + discover()

for n, pid in enumerate(dict.fromkeys(ids), 1):
    dest = os.path.join(RAW, f"{pid}.json")
    if os.path.exists(dest) and os.path.getsize(dest) > 50:
        continue
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--cookies",
        COOKIES,
        "--flat-playlist",
        "-J",
        "--no-warnings",
        "--sleep-requests",
        "1",
        "--retries",
        "3",
        f"https://www.youtube.com/playlist?list={pid}",
    ]
    p = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if p.returncode != 0 or not p.stdout.strip():
        print(f"FAIL {pid}: {p.stderr.strip()[:160]}", flush=True)
        continue
    open(dest, "w", encoding="utf-8").write(p.stdout)
    d = json.loads(p.stdout)
    print(
        f"[{n}/{len(ids)}] {pid} {d.get('title')} ({len(d.get('entries') or [])} entries)",
        flush=True,
    )
print("DONE")
