#!/usr/bin/env python3
"""Download the MHSVD source videos from their original platforms.

Reads videos/video_manifest.json and downloads every entry (or --missing-only:
entries not shipped in the archive) via yt-dlp, saving under the canonical
dataset filename so the annotations line up.

IDENTITY CHECK: the annotations are frame-indexed, so after each download the
frame count and frame rate are compared against the manifest (ffprobe needed).
Platforms occasionally re-encode old videos; on mismatch a warning is printed —
in that case use the archived copy of the video instead (see README).

Usage:
  python3 tools/download_videos.py [--missing-only] [--dest videos/files]
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def ffprobe_attrs(path):
    try:
        p = subprocess.run(
            ["ffprobe", "-v", "quiet", "-select_streams", "v:0", "-count_frames",
             "-show_entries", "stream=nb_read_frames,r_frame_rate,width,height",
             "-of", "json", str(path)], capture_output=True, text=True, timeout=300)
        s = json.loads(p.stdout)["streams"][0]
        num, den = s["r_frame_rate"].split("/")
        return {"frame_count": int(s.get("nb_read_frames") or 0),
                "frame_rate": round(int(num) / int(den), 2),
                "width": s["width"], "height": s["height"]}
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--missing-only", action="store_true",
                    help="only download entries not included in the archive")
    ap.add_argument("--dest", default=str(REPO / "videos" / "files"))
    args = ap.parse_args()
    if not shutil.which("yt-dlp"):
        sys.exit("yt-dlp is required: https://github.com/yt-dlp/yt-dlp")
    have_ffprobe = bool(shutil.which("ffprobe"))
    dest = Path(args.dest); dest.mkdir(parents=True, exist_ok=True)

    man = json.load(open(REPO / "videos" / "video_manifest.json"))
    todo = [v for v in man["videos"]
            if not (args.missing_only and v["distribution"] == "archive")]
    warn, fail = [], []
    for i, v in enumerate(todo, 1):
        name = v["file"] or f'{v["platform"]}_{v["video_id"]}.mp4'
        out = dest / name
        print(f"[{i}/{len(todo)}] {name}")
        if v.get("source_removed"):
            print("   SKIP: source removed from platform — use the archived copy")
            continue
        if out.exists():
            print("   exists, skipping download")
        else:
            r = subprocess.run(["yt-dlp", "-f", "mp4/bv*+ba/b", "-o", str(out), v["url"]])
            if r.returncode != 0:
                fail.append(name); print("   DOWNLOAD FAILED"); continue
        if have_ffprobe and v.get("media", {}).get("frame_count"):
            got = ffprobe_attrs(out)
            want = v["media"]
            if got and (got["frame_count"] != want["frame_count"]
                        or abs(got["frame_rate"] - float(want["frame_rate"])) > 0.51):
                warn.append(name)
                print(f"   WARNING: media mismatch (got {got['frame_count']}f@{got['frame_rate']}, "
                      f"annotations expect {want['frame_count']}f@{want['frame_rate']}) — "
                      f"prefer the archived copy for frame-accurate use")
    print(f"\nDONE: {len(todo)} processed, {len(fail)} failed, {len(warn)} media mismatches")
    if fail: print("failed:", *fail, sep="\n  ")
    if warn: print("mismatched:", *warn, sep="\n  ")

if __name__ == "__main__":
    main()
