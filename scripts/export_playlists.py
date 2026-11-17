"""Download every playlist of the account into raw/ (yt-dlp JSON dumps).

Run first; finalize_export.py then builds the canonical one-file-per-category export.
Cookies are NOT kept: regenerate with state2cookies.py, then delete cookies.txt.
"""

import json, os, subprocess, sys, time

# playlist titles contain Malayalam/Arabic; cp1252 consoles raise without this
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.environ.get("YT_ROOT", r"<repo>")
COOKIES = os.path.join(ROOT, "cookies.txt")
RAW = os.path.join(ROOT, "raw")
os.makedirs(RAW, exist_ok=True)

index = json.load(open(os.path.join(ROOT, "playlists.json"), encoding="utf-8"))
ids = ["WL"] + [p["playlist_id"] for p in index["playlists"]]

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
