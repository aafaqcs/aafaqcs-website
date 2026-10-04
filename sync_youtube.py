"""
Add new YouTube uploads to the website automatically (plain Python 3, no API key).

    python3 sync_youtube.py          # update data/*.json from the channel, then rebuild with build.py

Reads the channel's public feed (latest 15 uploads) and, when reachable, the /videos and /shorts pages. Each video
not already on the site is placed in a course by its title:
    "ML 07" ................ GATE DA · Machine Learning (fills the matching "coming soon" slot)
    "JKSSB" ................ JKSSB Computer Knowledge
    #shorts ................ Shorts
    "Lec 3.x", IP, subnet .. Computer Networks
    GATE DA ................ GATE DA · Start here
    anything else .......... Algorithm Arena
New full videos also get a "What's new" entry. Exit code 0 always; prints what changed.
"""

import html
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHANNEL = "UCbrkPZ63BAZFrMLBf0tWzHA"
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)", "Accept-Language": "en-US,en;q=0.9"}
NEWS_MAX = 10


def get(url, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=timeout).read()


def channel_videos():
    """{video_id: {"title", "short"}} from the feed, plus the channel pages when YouTube serves them."""
    vids = {}
    feed = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}").decode()
    for vid, title in re.findall(r"<yt:videoId>(.*?)</yt:videoId>.*?<title>(.*?)</title>", feed, re.S):
        vids[vid] = {"title": html.unescape(title), "short": None}
    for tab in ("videos", "shorts"):
        try:
            page = get(f"https://www.youtube.com/channel/{CHANNEL}/{tab}").decode("utf-8", "replace")
        except Exception:
            continue
        for vid in dict.fromkeys(re.findall(r'"videoId":"([\w-]{11})"', page)):
            vids.setdefault(vid, {"title": None, "short": None})
            if tab == "shorts":
                vids[vid]["short"] = True
    for vid, d in vids.items():
        if not d["title"]:
            try:
                d["title"] = json.loads(get(f"https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v={vid}"))["title"]
            except Exception:
                d["title"] = None
        if d["short"] is None:
            d["short"] = bool(d["title"] and re.search(r"#shorts?\b", d["title"], re.I))
    return {v: d for v, d in vids.items() if d["title"]}


def duration(vid):
    try:
        page = get(f"https://www.youtube.com/watch?v={vid}").decode("utf-8", "replace")
        s = int(re.search(r'"lengthSeconds":"(\d+)"', page).group(1))
        return f"{s // 60}:{s % 60:02d}"
    except Exception:
        return ""


def thumb(vid):
    out = ROOT / "assets" / "img" / f"yt_{vid}.jpg"
    if not out.exists():
        for q in ("maxresdefault", "sddefault", "hqdefault"):
            try:
                data = get(f"https://i.ytimg.com/vi/{vid}/{q}.jpg")
                if len(data) > 3000:
                    out.write_bytes(data)
                    break
            except Exception:
                pass
    return f"assets/img/yt_{vid}.jpg" if out.exists() else ""


def clean(title):
    t = re.sub(r"#\w+", "", title)
    t = re.split(r"\s+\|\s+", t)[0]
    t = re.sub(r"[\U0001F300-\U0001FAFF☀-➿️]", "", t)
    return re.sub(r"\s{2,}", " ", t).strip(" :|-")


def place(title, short):
    t = title.lower()
    if short:
        return "shorts", "SHORT"
    m = re.search(r"\bML\s*0?(\d{1,2})\b", title)
    if m:
        return "gate-da-ml", f"ML {int(m.group(1)):02d}"
    if "jkssb" in t:
        m = re.search(r"EP\s*:?\s*0?(\d+[A-C]?)", title, re.I)
        if not m:
            return "jkssb", ""
        num, letter = re.match(r"(\d+)([A-C]?)", m.group(1).upper()).groups()
        return "jkssb", f"EP{int(num):02d}{letter}"
    if re.search(r"\blec\s*3\.|\bip\b|ipv4|subnet|supernet|cidr|vlsm|routing|router|prefix match", t):
        return "networks", ""
    if "gate da" in t:
        return "gate-da", ""
    return "algorithms", ""


def main():
    courses = json.loads((ROOT / "data" / "courses.json").read_text())
    prof = json.loads((ROOT / "data" / "profile.json").read_text())
    C = {c["slug"]: c for c in courses["courses"]}
    on_site = {l["youtube"].rstrip("/").rsplit("/", 1)[-1] for c in courses["courses"] for l in c["lessons"] if l.get("youtube")}
    added = []
    for vid, d in reversed(list(channel_videos().items())):          # oldest first, so news ends up newest-first
        if vid in on_site:
            continue
        slug, code = place(d["title"], d["short"])
        course = C[slug]
        meta = " · ".join(x for x in (duration(vid), "Short" if d["short"] else "") if x)
        lesson = {"code": code, "title": clean(d["title"]), "youtube": f"https://youtu.be/{vid}", "status": "live", "thumb": thumb(vid), "meta": meta}
        slot = next((l for l in course["lessons"] if code and l.get("code") == code and l["status"] != "live"), None)
        if slot:                                                       # fill the matching "coming soon" slot
            slot.update({k: v for k, v in lesson.items() if v or k == "code"})
        else:
            course["lessons"].append(lesson)
            course["total"] = max(course.get("total", 0), len(course["lessons"]))
        added.append((slug, lesson))
        if not d["short"]:
            item = f"Released [{lesson['title']}]({lesson['youtube']}) in [{course['title']}](courses/{slug}.html)."
            prof["news"] = [item] + [n for n in prof["news"] if n != item]
    if not added:
        print("No new videos.")
        return
    prof["news"] = prof["news"][:NEWS_MAX]
    (ROOT / "data" / "courses.json").write_text(json.dumps(courses, indent=1, ensure_ascii=False) + "\n")
    (ROOT / "data" / "profile.json").write_text(json.dumps(prof, indent=1, ensure_ascii=False) + "\n")
    for slug, l in added:
        print(f"added to {slug}: {l['code'] + ' ' if l['code'] else ''}{l['title']}  {l['youtube']}")
    print(f"{len(added)} new video(s) on {date.today()}")


if __name__ == "__main__":
    main()
