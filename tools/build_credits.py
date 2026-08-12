#!/usr/bin/env python3
"""Generate CREDITS.md from the video manifest + sweep evidence (uploader names)."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
man = json.load(open(REPO / "videos" / "video_manifest.json"))
upl = {}
for f in (REPO / "tools" / "evidence").glob("*.json"):
    for r in json.load(open(f)):
        if r.get("uploader") or r.get("title"):
            upl[r["url"].strip()] = {"uploader": r.get("uploader"), "title": r.get("title")}

lines = [
    "# MHSVD — Source Video Credits",
    "",
    man["collection_license_statement"] + ".",
    "All videos remain the property of their respective creators; we gratefully acknowledge them for publishing under Creative Commons terms.",
    "",
    "| # | Video | Creator/Channel | Source | License at collection | Verified 2026-08-12 |",
    "|---|-------|-----------------|--------|----------------------|---------------------|",
]
for i, v in enumerate(man["videos"], 1):
    info = upl.get(v["url"], {})
    title = (info.get("title") or (v["file"] or "").rsplit("_", 2)[0].split("_", 2)[-1].replace("_", " "))[:60]
    creator = info.get("uploader") or "—"
    lines.append(f"| {i} | {title} | {creator} | [{v['platform']}]({v['url']}) | CC BY (platform filter) | {v['license_verified_20260812']} |")
(REPO / "CREDITS.md").write_text("\n".join(lines) + "\n")
print(f"CREDITS.md written: {len(man['videos'])} entries")
