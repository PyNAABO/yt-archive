# YouTube Account Export — @teengeeks3 (2026-11-21)

Archive of the Google account **account**, YouTube channel **Teen Geeks 3**
([@teengeeks3](https://www.youtube.com/@teengeeks3)), extracted on 2026-11-21. The account was
signed into the shared browser profile as `authuser=3`; this folder is its archive, as with
[`../ne00sa/`](../ne00sa/README.md) and [`../PESGOALS/`](../PESGOALS/README.md).

## Files

| File | Contents | Count |
|---|---|---|
| `subscriptions.json` | every subscribed channel: @handle, channel id, name, URL, flat `handles[]` / `channel_ids[]` arrays | **0** |
| `watch_later.json` | Watch Later videos: id, title, channel, duration, views, age, URL | **505** |
| `playlists.json` | all playlists, each with its videos (same fields) | **132** playlists / **3,221** entries |

## Notes

- **Zero subscriptions.** `/feed/channels`, the InnerTube `browse {browseId: "FEchannels"}` call
  (including the sort-chip params) and `/feed/subscriptions` all came back empty, so
  `subscriptions.json` is a real zero, not a failed scrape. The empty JSON was written by hand in
  the same schema the scraper produces, because `export_subscriptions.py` exits with an error when
  it finds no channel cards.
- Most of the 132 playlists are **saved** from other channels (Python, ML, Telegram bots, web dev);
  the rest are owned (`Music - NAABO`, `GYM`, `RomSleep`, `Important`, `Yallah`, `Misc.`, …).
  `playlists.json` does not mark which is which — the account had no owned/saved flag in the dump.
- `Linux for hackers` (`PLJA9dZicBDKfchoaTzN5CoGHIFiDTuYpk`) exported with **0 entries**: the
  playlist is unavailable to yt-dlp even when signed in, so its contents are lost unless it comes back.
- 120 playlist entries have no title — YouTube hides those as private/deleted videos. They keep
  their id and URL, nothing else.
- Liked videos are not tracked, here or anywhere else in this repo (`LL` is skipped).
- No video files, no watch history, no cookies are stored here.
- Watch Later and the playlists are what the **channel** held at export time; the parent folder's
  export (`@muhammednabhan1763`) is a different account and keeps its own counts.

## Re-exporting

Same scripts as the parent folder, pointed at this one:

```powershell
$env:YT_ROOT  = '<repo>\teengeeks3'
$env:YT_STATE = 'C:\.playwright-mcp\yt_state_teengeeks3.json'
python ..\scripts\state2cookies.py
python ..\scripts\export_playlists.py
python ..\scripts\finalize_export.py
```

`export_playlists.py` reads the playlist ids from this folder's `playlists.json`, so an existing
export is enough to drive a refresh. The browser state must be saved while this account is signed
in; `refresh.ps1` in the parent folder points at the main account's state file and does not touch
this folder.

The playlist download takes about 10 minutes for 132 playlists — give the shell a long timeout, a
background run stopped after 120 s resumes cleanly from the existing `raw/` files.

`raw/` and `cookies.txt` are working artifacts, gitignored, and deleted after a run.
