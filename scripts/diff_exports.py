"""Report what changed in the archive since the last commit.

    python scripts/diff_exports.py             # working tree vs HEAD
    python scripts/diff_exports.py OLD_DIR     # working tree vs another export folder

Reads watch_later.json and playlists.json. Writes nothing.
"""

import json, os, subprocess, sys

ROOT = os.environ.get("YT_ROOT") or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


def from_git(name):
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "show", "HEAD:" + name],
            capture_output=True,
            check=True,
        ).stdout
        return json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return None


def from_dir(folder, name):
    p = os.path.join(folder, name)
    if not os.path.isfile(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def label(v):
    title = v.get("title") or "(no title)"
    return title + ("  [" + v["channel"] + "]" if v.get("channel") else "")


def diff_list(old, new, name):
    o = {v["id"]: v for v in (old or {}).get("videos", []) if v.get("id")}
    n = {v["id"]: v for v in (new or {}).get("videos", []) if v.get("id")}
    added = [n[i] for i in n if i not in o]
    removed = [o[i] for i in o if i not in n]
    print(f"{name}: {len(o)} -> {len(n)}   +{len(added)} / -{len(removed)}")
    for v in added[:20]:
        print("  + " + label(v))
    if len(added) > 20:
        print(f"  ... and {len(added) - 20} more added")
    for v in removed[:20]:
        print("  - " + label(v))
    if len(removed) > 20:
        print(f"  ... and {len(removed) - 20} more removed")


def diff_playlists(old, new):
    o = {p["playlist_id"]: p for p in (old or {}).get("playlists", [])}
    n = {p["playlist_id"]: p for p in (new or {}).get("playlists", [])}
    print(f"playlists: {len(o)} -> {len(n)}")
    for pid, p in n.items():
        title = p.get("title") or pid
        if pid not in o:
            print(f"  + {title} ({len(p.get('videos', []))} videos)")
            continue
        a = {v["id"] for v in p.get("videos", []) if v.get("id")}
        b = {v["id"] for v in o[pid].get("videos", []) if v.get("id")}
        if a != b:
            print(f"  {title}: +{len(a - b)} / -{len(b - a)}")
    for pid, p in o.items():
        if pid not in n:
            print(f"  - {p.get('title') or pid}")


def main():
    old_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if old_dir:
        old_wl, old_pl, src = (
            from_dir(old_dir, "watch_later.json"),
            from_dir(old_dir, "playlists.json"),
            old_dir,
        )
    else:
        old_wl, old_pl, src = (
            from_git("watch_later.json"),
            from_git("playlists.json"),
            "HEAD",
        )

    if old_wl is None and old_pl is None:
        print(f"No previous export found in {src}, nothing to compare.")
        return

    print(f"{src} -> {ROOT}\n")
    diff_list(old_wl, from_dir(ROOT, "watch_later.json"), "watch later")
    print()
    diff_playlists(old_pl, from_dir(ROOT, "playlists.json"))


if __name__ == "__main__":
    main()
