# YouTube Account Export — @PESGOALS-xc5vf (2026-11-19)

Archive of the Google account signed in as **@PESGOALS-xc5vf** ("MNM"), extracted on
2026-11-19 when the accounts were consolidated onto the main account in the parent folder.

## Files

| File | Contents | Count |
|---|---|---|
| `subscriptions.json` | every subscribed channel: @handle, channel id, name, URL, flat `handles[]` / `channel_ids[]` arrays | **98** |
| `watch_later.json` | Watch Later videos: id, title, channel, duration, views, age, URL | **351** |
| `playlists.json` | all playlists, each with its videos (same fields) | **19** playlists / **590** entries |

## Notes

- Liked videos are not tracked, here or anywhere else in this repo.
- No video files, no watch history, no cookies are stored here.
- The playlist count is 19, not 20: `/feed/playlists` also lists YouTube-generated radios
  (`RD…`), which cannot be downloaded and are skipped.

## Status: cleared 2026-11-20

The live account was wiped after this export was committed: **0 subscriptions**, **0 Watch Later
videos**, and all 19 playlists gone (2 owned → deleted, 17 saved from other channels → removed from
the library). Liked videos were left as they were. Watch Later and subscriptions grew between the
export and the wipe — the account held more channels than the 98 captured here, so this folder is a
snapshot, not a complete history.

## Re-exporting

Same scripts as the parent folder, pointed at this one:

```powershell
$env:YT_ROOT  = (Get-Location).Path   # this folder
$env:YT_STATE = 'C:\.playwright-mcp\yt_state_pesgoals.json'
python ..\scripts\state2cookies.py
python ..\scripts\export_playlists.py
python ..\scripts\finalize_export.py
```

The browser state must be saved while this account is signed in — `refresh.ps1` in the parent
folder points at the main account's state file, so it does not touch this folder.

`raw/` and `cookies.txt` are working artifacts and are gitignored; delete them after a run.
