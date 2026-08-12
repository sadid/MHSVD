#!/usr/bin/env bash
# Build the MHSVD video archive (tar.gz) for dataset-artifact hosting (e.g. Zenodo).
# Contents: archive-tier videos ONLY (license verified CC BY today, or source
# removed from the platform), their .description credit files, the manifest,
# credits, and a NOTICE. Link-only videos are NOT included.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="/Volumes/S980Pro2T/DTA/MED/data/DBs/VideoSumm/nthu-summ/videos"
DIST="$REPO/dist"
STAGE="$DIST/MHSVD_videos"
mkdir -p "$STAGE/videos"

python3 - "$REPO" "$SRC" "$STAGE" <<'EOF'
import json, shutil, sys
from pathlib import Path
repo, src, stage = map(Path, sys.argv[1:4])
man = json.load(open(repo/"videos"/"video_manifest.json"))
n = 0
for v in man["videos"]:
    if v["distribution"] != "archive" or not v["file"]:
        continue
    shutil.copy2(src/v["file"], stage/"videos"/v["file"])
    if v.get("description_file") and (src/v["description_file"]).exists():
        shutil.copy2(src/v["description_file"], stage/"videos"/v["description_file"])
    n += 1
print(f"staged {n} archive-tier videos")
EOF

cp "$REPO/videos/video_manifest.json" "$STAGE/"
cp "$REPO/CREDITS.md" "$STAGE/"
cat > "$STAGE/NOTICE.txt" <<'EOF'
MHSVD — Multi-Highlight Short Video Dataset: source-video archive.

All videos in this archive were selected through Vimeo's and YouTube's
Creative Commons (permissive) license filters at collection time (2022).
This archive contains only the videos whose permissive license was verified
again on 2026-08-12, plus videos that have since been removed from their
platform (and are therefore preserved here for reproducibility). Videos whose
uploaders have since changed or restricted their license terms are NOT
redistributed here; they are available via videos/video_manifest.json links
and tools/download_videos.py in the dataset repository.

Each video remains the property of its creator (see CREDITS.md and the
accompanying .description files). This archive is provided to facilitate
research reproducibility.
EOF

( cd "$STAGE/videos" && shasum -a 256 *.mp4 > ../sha256sums.txt )
TAR="$DIST/MHSVD_videos_v1.tar.gz"
tar -czf "$TAR" -C "$DIST" "MHSVD_videos"
echo "archive: $TAR ($(du -h "$TAR" | cut -f1))"
