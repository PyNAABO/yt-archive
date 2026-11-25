# YouTube Account Export (2026-11-16T17:07:36+05:30)

Local archive of the **@ne00sa** Google account's YouTube data, taken before the switch to a different
Google account for watching. **One file per category** - no duplicate formats.

> The account now in use (channel @muhammednabhan1763) is exported at the
> repository root (`../`). This folder is the old account's archive only.

## Files

| File | Contents | Count |
|---|---|---|
| `subscriptions.json` | every channel: @handle, channel id, name, URL, per-channel provenance + flat `handles[]` / `channel_ids[]` arrays | **1872** |
| `watch_later.json` | Watch Later videos: id, title, channel, duration, views, age, URL | **751** |
| `playlists.json` | all own playlists, each with its videos (same fields) | **57** playlists / 2580 entries |
| `..\scripts\` | the export scripts, re-runnable (see below) | - |

> Liked videos were exported once (1,017 entries) and removed on 2026-11-17 when likes stopped being
> tracked. They were also purged from git history, so a fresh clone does not contain them.

### Subscriptions: where the numbers come from

| Source | Channels | Notes |
|---|---|---|
| live scrape (2026-11-16) | 295 | signed-in account - has channel **names** + URLs |
| pasted handle lists (2 files) | 446 + 1330 | merged in, deduped by handle |

Union after dedupe: **1872** unique channels (199 scrape-only, 1577 pasted-only, 96 in both).
The original pasted `.txt` files were merged in and deleted; everything they held is in `subscriptions.json`.

### Notes / caveats

- Watch Later holds **751** entries, all with titles. The in-browser view only renders 744 (YouTube hides
  videos it marks unavailable); yt-dlp recovered the rest from the playlist payload.
  A WL diff shows **removals, not watches**: YouTube never auto-removes watched videos.
- Video **files** were not downloaded - links and metadata only.
- No watch history, no own-channel data, no session cookies (dropped on request).

## Re-running the export

1. Sign in to the **@ne00sa** Google account in the patchright browser.
2. Point `YT_ROOT` at this folder — without it the scripts write to the root (the main account):

   ```powershell
   $env:YT_ROOT = (Get-Location).Path   # this folder
   ```

3. `python ..\scripts\state2cookies.py` -> writes `cookies.txt` (delete it afterwards).
4. `python ..\scripts\export_playlists.py` -> downloads every playlist into `raw/` (yt-dlp JSON dumps).
5. `python ..\scripts\finalize_export.py` -> rebuilds the canonical files from `raw/`
   (`watch_later.json`, `playlists.json`). `subscriptions.json` is edited by hand
   when new channel lists arrive - just add the handles to it. Liked videos are no longer built.

`raw/` is a working directory, not part of the archive - delete it after a successful run.

## Re-importing to the new account

- **Subscriptions**: no YouTube API for bulk subscribe. Either open each URL in `subscriptions.json`
  (`channels[].url`) and hit Subscribe, or run a browser-automation script against the new account's session.
- **Playlists / Watch Later / Likes**: create the playlist in the new account, then save each video
  (`videos[].url`) into it. The YouTube Data API (`playlistItems.insert`) does this programmatically but
  needs an OAuth client.
