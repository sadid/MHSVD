#!/usr/bin/env bash
# Build the COMPLETE MHSVD video archive (v1.1+): all 117 videos in one tar.gz,
# with per-video credits (.description), manifest, checksums, and NOTICE.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="/Volumes/S980Pro2T/DTA/MED/data/DBs/VideoSumm/nthu-summ/videos"
DIST="$REPO/dist"
STAGE="$DIST/MHSVD_videos"
rm -rf "$STAGE"
mkdir -p "$STAGE/videos"

python3 - "$REPO" "$SRC" "$STAGE" <<'EOF'
import json, shutil, sys
from pathlib import Path
repo, src, stage = map(Path, sys.argv[1:4])
man = json.load(open(repo/"videos"/"video_manifest.json"))
n = 0
for v in man["videos"]:
    if not v["file"]:
        continue
    shutil.copy2(src/v["file"], stage/"videos"/v["file"])
    n += 1
for d in (repo/"videos"/"descriptions").glob("*.description"):
    shutil.copy2(d, stage/"videos"/d.name)
print(f"staged {n} videos + all descriptions")
EOF

cp "$REPO/videos/video_manifest.json" "$STAGE/"
cp "$REPO/CREDITS.md" "$STAGE/"
cat > "$STAGE/NOTICE.txt" <<'EOF'
MHSVD — Multi-Highlight Short Video Dataset: complete source-video archive (117 videos).

All 117 videos were selected through Vimeo's and YouTube's Creative Commons (permissive) license filters at the time of collection (2022); Creative Commons grants are irrevocable for copies obtained under them.
Per-video license status, as re-verified in August 2026 by an automated sweep and by the authors' manual browser checks, is recorded in video_manifest.json (evidence preserved in the dataset repository under tools/evidence/); every re-verified license is a Creative Commons variant that permits attributed, non-commercial redistribution.
Several videos are no longer available or no longer play on their source platform; they are preserved here for research reproducibility and are marked in the manifest.

Each video remains the property of its creator; see CREDITS.md and the per-video .description files for attribution.
This archive is provided to facilitate research reproducibility, for academic research purposes.
If you are a rights holder and prefer a video to be removed from this archive, please open an issue in the dataset repository.
EOF

( cd "$STAGE/videos" && shasum -a 256 *.mp4 > ../sha256sums.txt )
TAR="$DIST/MHSVD_videos_complete_v1.1.tar.gz"
tar -czf "$TAR" -C "$DIST" "MHSVD_videos"
echo "archive: $TAR ($(du -h "$TAR" | cut -f1))"
