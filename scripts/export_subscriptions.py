"""Refresh subscriptions.json from /feed/channels.

Opens the signed-in session saved at C:\\.playwright-mcp\\yt_state.json, scrolls the
subscriptions grid, keeps every channel already in subscriptions.json, and resolves
the channel id only for handles that are new. Channels that disappeared from the
live list are reported but NOT deleted - remove them by hand if you meant to.

    python scripts/export_subscriptions.py             # rewrite subscriptions.json
    python scripts/export_subscriptions.py --dry-run   # report only
"""

import json, os, re, sys, urllib.request
from datetime import datetime, timezone

ROOT = os.environ.get("YT_ROOT") or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
FILE = os.path.join(ROOT, "subscriptions.json")
STATE = r"C:\.playwright-mcp\yt_state.json"
FEED = "https://www.youtube.com/feed/channels"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"


def scrape():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=STATE, locale="en-US")
        page = context.new_page()
        page.goto(FEED, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        if page.query_selector("ytd-channel-renderer") is None:
            raise SystemExit(f"no channel cards on {FEED} - page says: {page.title()}")

        last = 0
        for _ in range(40):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(900)
            count = page.eval_on_selector_all(
                "ytd-channel-renderer", "els => els.length"
            )
            if count == last:
                break
            last = count

        rows = page.eval_on_selector_all(
            "ytd-channel-renderer",
            """els => els.map(el => {
                const a = el.querySelector('a#main-link, a#channel-title-link, a#link');
                const t = el.querySelector('#channel-title yt-formatted-string, #text');
                const name = (t && t.textContent) || (a && a.getAttribute('aria-label')) || '';
                return { href: a ? a.getAttribute('href') : '', name: name.trim() };
            })""",
        )
        browser.close()

    out = {}
    for r in rows:
        m = re.match(r"^/@([^/?#]+)", r["href"] or "")
        if m:
            out[m.group(1)] = r["name"] or m.group(1)
    return out


def resolve_id(handle):
    req = urllib.request.Request(
        f"https://www.youtube.com/@{handle}",
        headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r'"channelId":"(UC[\w-]{22})"', html) or re.search(
        r'"externalId":"(UC[\w-]{22})"', html
    )
    return m.group(1) if m else None


def main():
    dry = "--dry-run" in sys.argv
    doc = json.load(open(FILE, encoding="utf-8"))
    old = {c["handle"].lower(): c for c in doc["channels"]}

    live = scrape()
    print(f"live subscriptions: {len(live)}")

    added = [h for h in live if h.lower() not in old]
    gone = [h for h in old if h not in {x.lower() for x in live}]
    for h in added:
        print(f"  + @{h}  {live[h]}")
    for h in gone:
        print(f"  - @{old[h]['handle']}  (kept in the file)")

    if dry:
        print("dry run, nothing written")
        return

    stamp = "scrape " + datetime.now().strftime("%Y-%m-%d")
    for h in added:
        cid = resolve_id(h)
        if not cid:
            print(f"  ! could not resolve a channel id for @{h}")
        old[h.lower()] = {
            "handle": h,
            "channel_id": cid,
            "name": live[h],
            "url": "https://www.youtube.com/@" + h,
            "sources": [stamp],
        }

    channels = sorted(old.values(), key=lambda c: c["handle"].lower())
    doc["generated_at"] = (
        datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    )
    doc["channels"] = channels
    doc["handles"] = [c["handle"] for c in channels]
    doc["channel_ids"] = [c["channel_id"] for c in channels if c.get("channel_id")]
    doc["counts"] = {
        "unique_channels": len(channels),
        "with_handle": sum(1 for c in channels if c.get("handle")),
        "with_channel_id": sum(1 for c in channels if c.get("channel_id")),
    }
    doc.setdefault("sources", {})[stamp] = (
        f"{len(live)} channels scraped live from /feed/channels"
    )

    if not added and not gone:
        print("no change, file untouched")
        return
    json.dump(doc, open(FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(
        f"subscriptions.json: {doc['counts']['unique_channels']} channels (+{len(added)} resolved)"
    )


if __name__ == "__main__":
    main()
