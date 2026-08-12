# MHSVD — Multi-Highlight Short Video Dataset

MHSVD is a keyframe-selection benchmark of **117 short-form ("transitory") videos** annotated by **three independent annotators**, introduced in:

> S. Sahami, G. Cheung, and C.-W. Lin, "Graph Unfolding and Sampling for Transitory Video Keyframe Selection via Gershgorin Disc Alignment," *IEEE Transactions on Image Processing*, 2026. (accepted)

Each annotator watched every video in full and selected up to 7 keyframes ("highlights") per video, using a video-annotation platform (Labelbox, whose research/education program we gratefully acknowledge).

## Contents

| Path | Description |
|------|-------------|
| `annotations/MHSVD_Annotator{1,2,3}.json` | Per-annotator keyframe annotations (one datarow per video, keyed by `video_file`; frame-indexed) |
| `videos/video_manifest.json` | Per-video record: canonical filename, source URL, license (at collection & verified 2026-08-12), media attributes (frame count/rate, resolution), SHA-256 of the reference copy, distribution tier |
| `videos/video_links.txt` | Plain list of the 117 source URLs |
| `tools/download_videos.py` | Downloads the source videos under their canonical filenames and verifies frame count/rate against the manifest (`yt-dlp` + `ffprobe`) |
| `tools/build_*.py|sh` | Scripts that generated this release from the internal sources (provenance) |
| `tools/evidence/` | Raw platform-license sweep results (2026-08-12) |
| `CREDITS.md` | Per-video creator credits |

## Videos: licensing and distribution

**All 117 videos were selected through Vimeo's and YouTube's Creative Commons (permissive) license filters at the time of collection (2022).**

The **complete video archive** (`MHSVD_videos_complete_v1.1.tar.gz`, see the [releases page](../../releases)) contains all 117 videos in one download, together with per-video credits, the manifest, and SHA-256 checksums.
This is the recommended way to obtain the dataset: several source videos are no longer available (or no longer play) on their platform, and platform re-encodes can change frame counts, whereas the archive holds the exact reference copies the annotations were made on.

Per-video license status, as re-verified in August 2026 (automated sweep + the authors' manual browser checks; evidence in `tools/evidence/`), is recorded in `videos/video_manifest.json`; every re-verified license is a Creative Commons variant permitting attributed, non-commercial redistribution.
Videos can alternatively be fetched from their original sources with `tools/download_videos.py`; the manifest's frame count/rate and SHA-256 fields let you verify any copy against the annotated reference.
If you are a rights holder and prefer a video to be removed from the archive, please open an issue.

The annotations themselves are our own work and are released under **CC BY 4.0** — cite the paper above when using them.

## Annotation format (brief)

Each entry in `annotations/MHSVD_Annotator*.json`:

- `data_row.video_file` — canonical video filename (join key with the manifest)
- `media_attributes` — frame count, frame rate, width/height
- `key_frame_feature_map` / `segments` — selected keyframes per annotation feature (frame indices), as exported from the annotation platform

`tools/` includes loading helpers used in the paper's evaluation pipeline.

## Evaluation protocol

The paper evaluates with the one-to-one keyframe-matching protocol (each selected keyframe matched to at most one ground-truth keyframe per annotator; see the paper, Sec. VII). Human-performance reference numbers are computed by evaluating each annotator against the remaining two.

## License summary

- **Annotations, manifest, scripts:** CC BY 4.0 (attribution: the paper above)
- **Videos:** property of their respective creators; collected under platform CC-BY filters (2022); redistribution policy as described above; see `videos/video_manifest.json` and `CREDITS.md` for per-video status
- The collection is only for academic research purposes.
