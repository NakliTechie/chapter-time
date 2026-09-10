#!/usr/bin/env python3
"""Build data/chapters-k5.js from the abhyas knowledge graph (read-only source).

Chapter Time uses only the concept spine (concepts.json), plus an optional
curated-video map. Subject-agnostic: branding is driven by meta.subject/grades.
Run from the chapter-time repo root:  python3 tools/build-data.py
"""
import json, os, sys

SRC = os.environ.get("ABHYAS_SRC", os.path.expanduser("~/Code/abhyas/content/maths/k5"))
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "chapters-k5.js")
# curated video lessons live here so a rebuild does not clobber them:
VIDEOS = os.path.join(os.path.dirname(__file__), "..", "data", "videos.json")


def main():
    cj_path = os.path.join(SRC, "concepts.json")
    if not os.path.exists(cj_path):
        sys.exit(f"abhyas concepts.json not found under {SRC} (set ABHYAS_SRC)")
    with open(cj_path) as f:
        cj = json.load(f)

    videos = {}
    if os.path.exists(VIDEOS):
        with open(VIDEOS) as f:
            videos = json.load(f)

    meta = dict(cj.get("meta", {}))
    meta.setdefault("subject", "Mathematics")

    bundle = {
        "meta": meta,
        "concepts": cj["concepts"],
        "videos": videos,  # { "<concept_id>": {"youtubeId": "...", "title": "..."} }
        "snapshot_source": "NakliTechie/abhyas content/maths/k5 concepts.json (read-only)",
    }

    out = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("/* Chapter spine from the abhyas KG (concepts.json). Generated — do not hand-edit. */\n")
        f.write("window.CHAPTER_DATA = ")
        json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print(f"wrote {out} ({os.path.getsize(out)/1024:.1f} KB) · concepts: {len(bundle['concepts'])} "
          f"· videos: {len(videos)} · subject: {meta['subject']}")


if __name__ == "__main__":
    main()
