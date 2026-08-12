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

THIS ARCHIVE IS NOT THE COMPLETE VIDEO SET: it contains 47 of the 117 dataset videos.
To obtain the full dataset, also run tools/download_videos.py --missing-only from the dataset repository, which fetches the remaining 70 videos from their original platforms.

All 117 videos were selected through Vimeo's and YouTube's Creative Commons (permissive) license filters at collection time (2022).
This archive redistributes only (a) the 43 videos whose permissive (CC BY) license was re-verified on 2026-08-12, and (b) the 4 videos that have since been removed from their platform — those 4 exist only in this archive and cannot be obtained anywhere else.
Videos whose uploaders have since changed or restricted their license terms are NOT redistributed here, out of respect for those changes; they are available from their original sources via the repository's manifest and downloader.

Each video remains the property of its creator (see CREDITS.md and the accompanying .description files).
This archive is provided to facilitate research reproducibility, for academic research purposes.
EOF

( cd "$STAGE/videos" && shasum -a 256 *.mp4 > ../sha256sums.txt )
TAR="$DIST/MHSVD_videos_v1.tar.gz"
tar -czf "$TAR" -C "$DIST" "MHSVD_videos"
echo "archive: $TAR ($(du -h "$TAR" | cut -f1))"
