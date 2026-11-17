# YouTube Account Export — @muhammednabhan1763 (2026-11-17)

Local archive of the YouTube channel
[@muhammednabhan1763](https://www.youtube.com/@muhammednabhan1763) — the account in use from 2026-11-17.
**Main account — this folder's root.** The old **@ne00sa** export sits in [`ne00sa/`](ne00sa/README.md).

**One file per category**, JSON only.

## Live page

<https://pynaabo.github.io/yt-archive/> — picks a random video from `watch_later.json` (Space or → for another).
Source: <https://github.com/PyNAABO/yt-archive>.

## Files

| File | Contents | Count |
|---|---|---|
| `subscriptions.json` | every subscribed channel: @handle, channel id, name, URL, flat `handles[]` / `channel_ids[]` arrays | **40** |
| `watch_later.json` | Watch Later videos: id, title, channel, duration, views, age, URL | **382** |
| `liked_videos.json` | Liked videos (same fields) | **693** |
| `playlists.json` | all playlists, each with its videos (same fields) | **21** playlists / **5578** entries |

## Caveats

- `playlists.json` includes **only** playlists — Watch Later and Liked videos live in their own files.
- "Out Of Focus - Web Special" reports **4,999 episodes**; that is YouTube's own count, not an export bug.
- `SS` ("Sounds") is a YouTube-generated private playlist; it holds 1 entry.
- Subscriptions were scraped from `/feed/channels` — the channel IDs were resolved one by one, so every
  channel has both a handle and a `UC…` id.
- No video files, no watch history, no cookies are stored here.

## Re-running the export

Scripts live in `scripts\` and default to this folder:

```powershell
$D = 'C:\Users\mhodn\Desktop\Essentials\NAABO\YouTube'
python "$D\scripts\state2cookies.py"     # writes cookies.txt here (delete it afterwards)
python "$D\scripts\export_playlists.py"  # downloads every playlist into raw/
python "$D\scripts\finalize_export.py"   # rebuilds watch_later / liked_videos / playlists
```

To re-export the **old** account instead, set `$env:YT_ROOT = "$D\ne00sa"` before running.

`export_playlists.py` reads the playlist ids from `playlists.json` in this folder, so an existing export
is enough to drive a refresh. `subscriptions.json` is not regenerated — re-scrape `/feed/channels` and
rebuild it if subscriptions changed.

`raw/` is a working directory, not part of the archive — delete it after a successful run.
