#!/usr/bin/env python3
"""Produce the release annotation files from the internal Concise2 exports.

Transformation is MINIMAL and verified:
  1. data_row.row_data (internal S3 URL) -> replaced by the video filename
  2. data_row.details (all-empty fields) and internal data_row.id dropped
  3. everything else byte-faithful (keyframe maps, segments, media attributes)

A deep-verification pass asserts that, apart from the two intended edits,
the output is identical to the source.
"""
import json, copy
from pathlib import Path

SRC = Path("/Volumes/S980Pro2T/DTA/MED/data/DBs/VideoSumm/nthu-summ/highlight_summaries")
REPO = Path(__file__).resolve().parent.parent

for a in (1, 2, 3):
    src = json.load(open(SRC / f"Export_Concise2_MHSD_Annotator{a}.json"))
    out = copy.deepcopy(src)
    for d in out:
        dr = d["data_row"]
        dr["video_file"] = dr.pop("external_id")
        dr.pop("row_data", None)
        dr.pop("details", None)
        dr.pop("id", None)
    # verify: reverting the intended edits reproduces the source exactly
    chk = copy.deepcopy(out)
    for c, s in zip(chk, src):
        c["data_row"]["external_id"] = c["data_row"].pop("video_file")
        c["data_row"]["row_data"] = s["data_row"]["row_data"]
        c["data_row"]["details"] = s["data_row"]["details"]
        c["data_row"]["id"] = s["data_row"]["id"]
        # restore key order for comparison
        c["data_row"] = {k: c["data_row"][k] for k in s["data_row"]}
    assert chk == src, f"Annotator{a}: unintended difference!"
    dst = REPO / "annotations" / f"MHSVD_Annotator{a}.json"
    dst.write_text(json.dumps(out, indent=1))
    print(f"OK {dst.name}: {len(out)} datarows (verified faithful)")
print("DONE")
