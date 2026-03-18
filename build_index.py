"""
build_index.py — מייצר קבצי אינדקס קלים + קבצי יחידת-טקסט לטעינה מהירה

ריצה:
    python build_index.py               # כל *-Gnizah.json בתיקייה הנוכחית
    python build_index.py file1.json    # קבצים ספציפיים

תוצרים לכל קובץ X-Gnizah.json:
    X-index.json          ~200 KB  — אינדקס קל (מזהים + ציונים)
    X-units/              תיקייה  — קובץ JSON לכל יחידת-טקסט (~50-200 KB כ"א)
"""

import json
import os
import glob
import sys
import time


def get_candidate_score(c):
    for key in ('alignment_score', 'norm_score', 'score'):
        v = c.get(key)
        if v is not None and isinstance(v, (int, float)) and v == v:  # not NaN
            return v
    return 0


def extract_location(cand):
    """ממצה את מזהה קטע הגניזה מהמועמד."""
    loc = cand.get('location')
    if loc:
        return loc
    ad = cand.get('alignment_details') or cand.get('reuse_details') or {}
    if isinstance(ad, str):
        try:
            ad = json.loads(ad)
        except Exception:
            return cand.get('elastic_id', '')
    if isinstance(ad, list):
        ad = ad[0] if ad else {}
    if isinstance(ad, dict):
        return ad.get('location') or cand.get('elastic_id', '')
    return cand.get('elastic_id', '')


def build_index(json_path):
    json_path = os.path.abspath(json_path)
    base = os.path.splitext(os.path.basename(json_path))[0]   # e.g. "Devarim_Rabbah-Gnizah"
    name = base.replace('-Gnizah', '').replace('-gnizah', '')  # e.g. "Devarim_Rabbah"
    dir_path = os.path.dirname(json_path)
    units_dir = os.path.join(dir_path, name + '-units')

    os.makedirs(units_dir, exist_ok=True)

    print(f"\n▶ עיבוד: {os.path.basename(json_path)}")
    t0 = time.time()

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    print(f"  {total:,} יחידות טקסט טעונות ({time.time()-t0:.1f}s)")

    index = {}
    t1 = time.time()

    for i, (uid, unit) in enumerate(data.items()):
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{total} ({int((i+1)/total*100)}%)...")

        # מיצוי רשימת מועמדים
        cands_raw = (unit.get('candidates')
                     or unit.get('matches')
                     or unit.get('results')
                     or [])
        if isinstance(cands_raw, dict):
            cands_raw = list(cands_raw.values())

        # אינדקס קל — ציון + מזהה בלבד
        light_cands = []
        for c in cands_raw:
            light_cands.append({
                'elastic_id':        c.get('elastic_id', ''),
                'location':          extract_location(c),
                'alignment_score':   c.get('alignment_score'),
                'norm_score':        c.get('norm_score'),
                'score':             c.get('score'),
                'full_alignment_ind':c.get('full_alignment_ind', 0),
                'text_reuse_ind':    bool(c.get('text_reuse_ind', False)),
                'in_process':        c.get('in_process', 0),
            })

        index[uid] = {
            'job_id':    unit.get('job_id'),
            'Location':  unit.get('Location', uid),
            'candidates': light_cands,
        }

        # קובץ יחידה מלא
        unit_path = os.path.join(units_dir, uid + '.json')
        with open(unit_path, 'w', encoding='utf-8') as f:
            json.dump(unit, f, ensure_ascii=False, separators=(',', ':'))

    # כתיבת האינדקס
    index_path = os.path.join(dir_path, name + '-index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))

    idx_kb  = os.path.getsize(index_path) // 1024
    full_kb = os.path.getsize(json_path)  // 1024
    reduction = int((1 - idx_kb / full_kb) * 100)
    print(f"  ✓ אינדקס: {name}-index.json  ({idx_kb:,} KB — {reduction}% קטן יותר מהמקור)")
    print(f"  ✓ יחידות: {name}-units/  ({total:,} קבצים)")
    print(f"  סה\"כ זמן: {time.time()-t1:.1f}s")


if __name__ == '__main__':
    paths = sys.argv[1:] if len(sys.argv) > 1 else glob.glob('*-Gnizah.json')

    if not paths:
        print("לא נמצאו קבצי *-Gnizah.json בתיקייה הנוכחית.")
        print("שימוש: python build_index.py [file1.json file2.json ...]")
        sys.exit(1)

    for p in paths:
        if not os.path.isfile(p):
            print(f"קובץ לא נמצא: {p}")
            continue
        build_index(p)

    print("\n✅ האינדקסים מוכנים. כעת פתח את index.html ובחר את התיקייה.")
