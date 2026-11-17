"""Build the canonical export from raw/ yt-dlp dumps + the merged subscriptions file.

Outputs exactly one file per category (no CSV/TXT twins, no manifest):
    subscriptions.json  watch_later.json  playlists.json  README.md
Liked videos are not exported.
"""

import json, os, glob, datetime

ROOT = os.environ.get("YT_ROOT", r"C:\Users\mhodn\Desktop\Essentials\NAABO\YouTube")
RAW = os.path.join(ROOT, "raw")
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def load_raw(pid):
    p = os.path.join(RAW, f"{pid}.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    return json.loads(d) if isinstance(d, str) else d


def cache_by_id():
    p = os.path.join(ROOT, "watch_later.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    return {v["id"]: v for v in d.get("videos", []) if v.get("id")}


def build(d, cache, label):
    videos = []
    for e in d.get("entries") or []:
        if not e:
            continue
        c = cache.get(e.get("id"), {})
        videos.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "channel": e.get("channel") or e.get("uploader"),
                "channel_id": e.get("channel_id"),
                "duration": e.get("duration"),
                "view_count": e.get("view_count"),
                "views": c.get("views"),
                "age": c.get("age"),
                "url": e.get("url")
                or (
                    f"https://www.youtube.com/watch?v={e['id']}"
                    if e.get("id")
                    else None
                ),
            }
        )
    return {
        "label": label,
        "playlist_id": d.get("id"),
        "url": d.get("webpage_url")
        or f"https://www.youtube.com/playlist?list={d.get('id')}",
        "count": len(videos),
        "generated_at": now,
        "videos": videos,
    }


cache = cache_by_id()

wl = load_raw("WL")
if wl:
    obj = build(wl, cache, "Watch later")
    obj["note"] = "entries without a title are videos YouTube hides as unavailable"
    json.dump(
        obj,
        open(os.path.join(ROOT, "watch_later.json"), "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=1,
    )
    print("watch_later.json:", obj["count"])

own = []
seen_own = set()
for p in sorted(glob.glob(os.path.join(RAW, "PL*.json"))) + sorted(
    glob.glob(os.path.join(RAW, "*.json"))
):
    pid = os.path.splitext(os.path.basename(p))[0]
    if pid in ("WL", "LL") or pid in seen_own:
        continue
    d = load_raw(pid)
    if not d:
        continue
    seen_own.add(pid)
    obj = build(d, cache, d.get("title") or pid)
    own.append(obj)
if own:
    pl = {
        "generated_at": now,
        "count": len(own),
        "total_video_entries": sum(o["count"] for o in own),
        "playlists": own,
    }
    json.dump(
        pl,
        open(os.path.join(ROOT, "playlists.json"), "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=1,
    )
    print(
        "playlists.json:",
        pl["count"],
        "playlists /",
        pl["total_video_entries"],
        "entries",
    )
