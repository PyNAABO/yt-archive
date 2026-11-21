# YouTube Account Export — @muhammednabhan1763 (2026-11-17)

Local archive of the YouTube channel
[@muhammednabhan1763](https://www.youtube.com/@muhammednabhan1763) — the account in use from 2026-11-17.
**Main account — this folder's root.** Older accounts are archived in subfolders:
[`ne00sa/`](ne00sa/README.md), [`PESGOALS/`](PESGOALS/README.md) and
[`teengeeks3/`](teengeeks3/README.md). Only this root account is refreshed now.

**One file per category**, JSON only.

## Live page

<https://pynaabo.github.io/yt-archive/> — picks a random video from `watch_later.json` (Space or → for another).
Source: <https://github.com/PyNAABO/yt-archive>.

## Files

| File | Contents | Count |
|---|---|---|
| `subscriptions.json` | every subscribed channel: @handle, channel id, name, URL, flat `handles[]` / `channel_ids[]` arrays | **40** |
| `watch_later.json` | Watch Later videos: id, title, channel, duration, views, age, URL | **382** |
| `playlists.json` | all playlists, each with its videos (same fields) | **21** playlists / **5578** entries |

## Caveats

- `playlists.json` includes **only** playlists — Watch Later lives in its own file.
- Liked videos are **not** exported or tracked.
- "Out Of Focus - Web Special" reports **4,999 episodes**; that is YouTube's own count, not an export bug.
- `SS` ("Sounds") is a YouTube-generated private playlist; it holds 1 entry.
- Subscriptions were scraped from `/feed/channels` — the channel IDs were resolved one by one, so every
  channel has both a handle and a `UC…` id.
- No video files, no liked videos, no watch history, no cookies are stored here.

## Re-running the export

One command does the whole cycle — cookies, download, rebuild, sanity check, commit, push:

```powershell
.\scripts\refresh.ps1              # this folder (main account)
.\scripts\refresh.ps1 -SkipPush    # commit only
```

It turns the saved browser session (`C:\.playwright-mcp\yt_state.json`) into `cookies.txt`, downloads
every playlist into `raw/`, rebuilds `watch_later.json` and `playlists.json`, **refuses to commit** if
Watch Later shrank by more than half, deletes the cookies and `raw/`, then commits and pushes.

The individual steps, if you want them by hand:

```powershell
$D = '<repo>'
python "$D\scripts\state2cookies.py"     # writes cookies.txt here (delete it afterwards)
python "$D\scripts\export_playlists.py"  # downloads every playlist into raw/
python "$D\scripts\finalize_export.py"   # rebuilds watch_later / playlists
```

To re-export the **old** account instead, add `-Root "$D\ne00sa"` to `refresh.ps1`, or set
`$env:YT_ROOT = "$D\ne00sa"` before running the individual scripts.

`export_playlists.py` reads the playlist ids from `playlists.json` in this folder, so an existing export
is enough to drive a refresh. `subscriptions.json` is not regenerated — re-scrape `/feed/channels` and
rebuild it if subscriptions changed.

`raw/` is a working directory, not part of the archive — delete it after a successful run.

## What changed since the last export

```powershell
python scripts\diff_exports.py            # working tree vs last commit
python scripts\diff_exports.py ne00sa     # working tree vs another folder
```

Prints added/removed Watch Later entries and per-playlist deltas. Reads only, writes nothing.

## Retiring an account (after its export is committed)

Clearing the live account is browser-only work. Replaying `cookies.txt` from Python gets redirected
to Google sign-in, and the subscribe button ignores synthetic clicks unless its confirmation dialog
is really visible. The pattern below was verified 2026-11-20 on the PESGOALS account:

1. Read `"SESSION_INDEX"` from the signed-in `/feed/channels` page source. That number goes in the
   `X-Goog-AuthUser` header. Without it every InnerTube call runs as the wrong Google account and
   returns 200 while doing nothing.
2. Unsubscribe through the UI, one channel at a time: click `#subscribe-button button`, wait for a
   **visible** `yt-confirm-dialog-renderer`, click its `Unsubscribe` button, wait for it to close.
   The dialog element is reused, so a loop that clicks a hidden copy reports success and removes
   nothing.
3. Empty Watch Later and remove playlists with InnerTube calls made **from the page** (real origin,
   `SAPISIDHASH` built from the `SAPISID` cookie): `browse/edit_playlist` with
   `ACTION_REMOVE_VIDEO_BY_VIDEO_ID` (20 ids per call) for Watch Later, `playlist/delete` for
   playlists the account owns, and `like/removelike` with `target.playlistId` for the ones it only
   saved — those answer 403 to delete.
4. Verify through the API, not the DOM: `browse {browseId: "FEchannels"}` keeps returning
   `channelRenderer` entries marked `"Subscribed"` while any subscription is left, even though the
   rendered page shows stale cards. Watch Later is empty when the playlist header says `No videos`
   (`browse {browseId: "VLWL"}`). `browse {browseId: "FEplaylists"}` answers **400 invalid argument**
   for this account type, so verify playlists on the page tabs: `Owned` should hold only Watch later,
   `Saved` only the `Mix - …` radios YouTube generates by itself.

Liked videos (`LL`) are system data and are left alone unless asked.
