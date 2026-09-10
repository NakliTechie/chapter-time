#!/usr/bin/env python3
"""Build data/chapters.js — the full multi-subject chapter catalog from the abhyas
knowledge graphs (read-only source). Scans every content/<subject>/<band>/concepts.json
the engine has emitted and bundles them into one window.CHAPTER_DATA.catalog.

Curated videos live in data/videos.json (concept-id -> {youtubeId,title,channel}) and
are folded into whichever graph contains that concept id. Do NOT edit the abhyas engine.
Run from the chapter-time repo root:  python3 tools/build-data.py
"""
import os, sys, json, datetime

ROOT = os.environ.get("ABHYAS_CONTENT", os.path.expanduser("~/Code/abhyas/content"))
HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "data", "chapters.js")
VIDEOS = os.path.join(HERE, "..", "data", "videos.json")

# Display order: band (K5 before 6-10), then subject.
BAND_ORDER = ["K5", "6-10"]
BAND_LABEL = {"K5": "Class 1–5", "6-10": "Class 6–10"}
SUBJECT_ORDER = ["Mathematics", "Physics", "Chemistry", "Biology", "EVS",
                 "English", "History", "Geography", "Civics", "Economics"]


def load_videos():
    if not os.path.exists(VIDEOS):
        return {}
    v = json.load(open(VIDEOS))
    return {k: val for k, val in v.items() if not k.startswith("_")}


def main():
    if not os.path.isdir(ROOT):
        sys.exit(f"abhyas content not found at {ROOT} (set ABHYAS_CONTENT)")
    videos = load_videos()

    catalog = []
    for subject_dir in sorted(os.listdir(ROOT)):
        sp = os.path.join(ROOT, subject_dir)
        if not os.path.isdir(sp) or subject_dir in ("test",):
            continue
        for band_dir in sorted(os.listdir(sp)):
            bp = os.path.join(sp, band_dir)
            cj = os.path.join(bp, "concepts.json")
            if not os.path.isdir(bp) or not os.path.exists(cj):
                continue
            try:
                d = json.load(open(cj))
            except Exception as e:
                print(f"  skip {subject_dir}/{band_dir}: {e}")
                continue
            concepts = d.get("concepts", [])
            if not concepts:
                continue
            meta = d.get("meta", {})
            subject = meta.get("subject") or subject_dir.title()
            band = meta.get("band") or band_dir
            grades = sorted({c.get("grade") for c in concepts if c.get("grade") is not None})
            gvideos = {c["id"]: videos[c["id"]] for c in concepts if c["id"] in videos}
            catalog.append({
                "id": f"{subject_dir}-{band_dir}",
                "subject": subject,
                "band": band,
                "bandLabel": BAND_LABEL.get(band, band),
                "grades": grades,
                "concepts": concepts,
                "videos": gvideos,
            })

    def sort_key(e):
        b = BAND_ORDER.index(e["band"]) if e["band"] in BAND_ORDER else 99
        s = SUBJECT_ORDER.index(e["subject"]) if e["subject"] in SUBJECT_ORDER else 99
        return (b, s, e["subject"])
    catalog.sort(key=sort_key)

    bundle = {
        "generatedAt": datetime.date.today().isoformat(),
        "catalog": catalog,
        "snapshot_source": "NakliTechie/abhyas content/*/*/concepts.json (read-only)",
    }
    out = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("/* Full chapter catalog from the abhyas knowledge graphs. Generated — do not hand-edit. */\n")
        f.write("window.CHAPTER_DATA = ")
        json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    total = sum(len(e["concepts"]) for e in catalog)
    vids = sum(len(e["videos"]) for e in catalog)
    print(f"wrote {out} ({os.path.getsize(out)/1024:.1f} KB)")
    print(f"catalog: {len(catalog)} graphs · {total} concepts · {vids} curated videos")
    for e in catalog:
        print(f"  {e['id']:16} {e['subject']:12} {e['band']:5} {len(e['concepts']):>4} concepts, {len(e['videos'])} videos")


if __name__ == "__main__":
    main()
