#!/usr/bin/env python3
"""Build videos/video_manifest.json for the MHSVD release.

Sources (author machine):
  - dataset home: videos/ + video_links.txt  (SRC below)
  - annotation export (media attributes + external_id join)
  - license sweep evidence JSONs (tools/evidence/), collected 2026-08-12

Every entry carries `license_at_collection`: all videos were selected through
Vimeo/YouTube's Creative Commons (permissive) license filters at collection
time (2022); CC licenses are irrevocable for copies obtained under them.
`license_verified_20260812` records the platform-reported license as of the
sweep date, out of respect for uploaders' later changes: only entries whose
permissive license is verifiable today (or whose source has been removed,
making the link unusable) are included in the video archive; all others are
distributed as link + downloader.
"""
import json, hashlib, re, sys, glob
from pathlib import Path

SRC = Path("/Volumes/S980Pro2T/DTA/MED/data/DBs/VideoSumm/nthu-summ")
REPO = Path(__file__).resolve().parent.parent
EVID = REPO / "tools" / "evidence"

CLAIM = "CC BY (selected via the platform's Creative Commons license filter at collection time, 2022)"

def vid_id(url):
    m = re.search(r'vimeo\.com/(\d+)', url)
    if m: return "vimeo", m.group(1)
    m = re.search(r'(?:v=|youtu\.be/)([\w-]+)', url)
    if m: return "youtube", m.group(1)
    raise ValueError(url)

# license evidence
lic_today = {}
for f in EVID.glob("*.json"):
    for r in json.load(open(f)):
        url = r["url"].strip()
        if "error" in r and "license" not in r:
            lic_today[url] = {"status": "unreachable", "detail": r["error"][:80]}
        else:
            lic_today[url] = {"status": "ok", "license": r.get("license"),
                              "title": r.get("title"), "uploader": r.get("uploader")}

# media attributes via annotation export (identical across annotators)
ann = json.load(open(SRC / "highlight_summaries" / "Export_Concise2_MHSD_Annotator1.json"))
media = {d["data_row"]["external_id"]: d["media_attributes"] for d in ann}

files = sorted(p.name for p in (SRC / "videos").glob("*.mp4"))
links = [u.strip() for u in open(SRC / "video_links.txt") if u.strip()]

def norm_lic(v):
    if v is None: return None
    s = str(v).lower()
    if "creative commons attribution license" in s or s == "by": return "CC BY"
    if s.startswith("by-"): return "CC " + s.upper().replace("BY-", "BY-")
    if "standard" in s: return "standard"
    return str(v)

def sanitized(vid):
    # the 2022 downloader replaced '-' with '_' in filenames and dropped a leading '-'
    return vid.replace("-", "_").lstrip("_")

rows, used = [], set()
for url in links:
    plat, vid = vid_id(url)
    sv = sanitized(vid)
    match = [f for f in files
             if f"_{vid}_" in f or f.startswith(f"{plat}_{vid}_")
             or f"_{sv}_" in f or f.startswith(f"{plat}_{sv}_")]
    fname = match[0] if len(match) == 1 else None
    if fname: used.add(fname)
    ev = lic_today.get(url, {})
    lt = norm_lic(ev.get("license")) if ev.get("status") == "ok" else None
    dead = ev.get("status") == "unreachable"
    verified = (lt == "CC BY")
    entry = {
        "file": fname,
        "url": url,
        "platform": plat,
        "video_id": vid,
        "license_at_collection": CLAIM,
        "license_verified_20260812": ("unreachable" if dead else (lt or "unresolved")),
        "distribution": ("archive" if (verified or dead) else "link-only"),
        "source_removed": dead,
    }
    if fname:
        m = media.get(fname, {})
        entry["media"] = {k: m.get(k) for k in ("frame_count", "frame_rate", "width", "height", "mime_type")}
        h = hashlib.sha256()
        with open(SRC / "videos" / fname, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        entry["sha256"] = h.hexdigest()
        d = SRC / "videos" / fname.replace(".mp4", ".description")
        # description files are named after the pre-sanitize title; fall back by id
        if not d.exists():
            cand = [p for p in (SRC / "videos").glob("*.description") if f"_{vid}_" in p.name or vid in p.name]
            d = cand[0] if cand else None
        entry["description_file"] = d.name if d and d.exists() else None
    rows.append(entry)

unmatched = [f for f in files if f not in used]
out = {"dataset": "MHSVD (Multi-Highlight Short Video Dataset)",
       "collection_license_statement": CLAIM,
       "video_count": len(rows),
       "videos": rows}
(REPO / "videos" / "video_manifest.json").write_text(json.dumps(out, indent=1))
arch = sum(1 for r in rows if r["distribution"] == "archive")
print(f"manifest written: {len(rows)} entries | archive-tier={arch} link-only={len(rows)-arch}")
print(f"file-matched={sum(1 for r in rows if r['file'])} | unmatched files: {unmatched or 'none'}")
missing_media = [r['file'] for r in rows if r.get('file') and not r.get('media', {}).get('frame_count')]
print("entries missing media attrs:", missing_media or "none")
