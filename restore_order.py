"""
restore_order.py — שחזור סדר המפתחות באינדקס בהתאם לקבצי ה-Gnizah המקוריים.

שימוש:
    python restore_order.py <תיקיית-נתונים> <תיקיית-מקור>

    תיקיית-נתונים  = תיקייה עם קבצי *-index.json
    תיקיית-מקור    = תיקייה עם קבצי *-Gnizah.json המקוריים
"""
import json
import sys
import os

if len(sys.argv) < 3:
    print("שימוש: python restore_order.py <תיקיית-נתונים> <תיקיית-מקור>")
    print("  תיקיית-נתונים  = תיקייה עם קבצי *-index.json")
    print("  תיקיית-מקור    = תיקייה עם קבצי *-Gnizah.json המקוריים")
    sys.exit(1)

base = sys.argv[1]
orig_base = sys.argv[2]

pairs = [
    ('Midrash_Tanchuma-Gnizah.json', 'Midrash_Tanchuma-index.json'),
    ('Midrash_Tanchuma_Buber-Gnizah.json', 'Midrash_Tanchuma_Buber-index.json'),
]

for orig_fname, idx_fname in pairs:
    orig_path = os.path.join(orig_base, orig_fname)
    idx_path = os.path.join(base, idx_fname)

    if not os.path.isfile(orig_path):
        print(f"SKIP: {orig_fname} not found in {orig_base}")
        continue
    if not os.path.isfile(idx_path):
        print(f"SKIP: {idx_fname} not found in {base}")
        continue

    with open(orig_path, 'r', encoding='utf-8') as f:
        orig = json.load(f)
    with open(idx_path, 'r', encoding='utf-8') as f:
        idx = json.load(f)

    orig_keys = list(orig.keys())
    idx_keys_set = set(idx.keys())

    # Reorder index by original key order
    ordered = {}
    for k in orig_keys:
        if k in idx_keys_set:
            ordered[k] = idx[k]

    # Safety check: any keys in index but not in original?
    missing = idx_keys_set - set(orig_keys)
    if missing:
        print(f"WARNING: {len(missing)} keys in index but not in original for {idx_fname}")
        for k in missing:
            ordered[k] = idx[k]

    with open(idx_path, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, ensure_ascii=False)

    result_keys = list(ordered.keys())
    print(f"{idx_fname}: {len(result_keys)} keys, order matches original: {result_keys == orig_keys}")
    print(f"  First 5: {result_keys[:5]}")
    print()
