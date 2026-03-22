"""
reorder_index.py — סידור מחדש של קבצי אינדקס תנחומא/תנחומא בובר לפי סדר פרשיות התורה.

שימוש:
    python reorder_index.py                     # עובד על התיקייה הנוכחית
    python reorder_index.py <תיקיית-נתונים>     # תיקייה ספציפית
"""
import json
import re
import sys
import os

# Torah parsha order
PARSHA_ORDER = [
    "Bereshit", "Noach", "Lech_Lecha", "Vayera", "Chayei_Sara",
    "Toldot", "Vayetzei", "Vayishlach", "Vayeshev", "Miketz",
    "Vayigash", "Vayechi",
    "Shemot", "Vaera", "Bo", "Beshalach", "Yitro",
    "Mishpatim", "Terumah", "Tetzaveh", "Ki_Tisa", "Vayakhel", "Pekudei",
    "Vayikra", "Tzav", "Shmini", "Tazria", "Metzora",
    "Achrei_Mot", "Kedoshim", "Emor", "Behar", "Bechukotai",
    "Bamidbar", "Nasso", "Behaalotcha", "Shlach", "Korach",
    "Chukat", "Balak", "Pinchas", "Matot", "Masei",
    "Devarim", "Vaetchanan", "Eikev", "Reeh", "Shoftim",
    "Ki_Teitzei", "Ki_Tavo", "Nitzavim", "Vayeilech", "HaAzinu",
    "VZot_HaBerachah"
]

# Build lookup: parsha name -> index. Appendix entries go right after parent.
parsha_index = {}
for i, p in enumerate(PARSHA_ORDER):
    parsha_index[p] = i
    parsha_index[f"Appendix_to_{p}"] = i + 0.5


def sort_key_tanchuma(key):
    """Extract (parsha_order, section, subsection) for sorting."""
    m = re.search(r'Midrash_Tanchuma__(.+?)_(\d+)_(\d+)$', key)
    if m:
        parsha = m.group(1)
        section = int(m.group(2))
        subsection = int(m.group(3))
        order = parsha_index.get(parsha, 9999)
        return (1, order, section, subsection)

    m = re.search(r'Otzar_Midrashim__Midrash_Tanchuma_(\d+)$', key)
    if m:
        num = int(m.group(1))
        return (0, 0, num, 0)

    return (2, 9999, 0, 0)


def sort_key_tanchuma_buber(key):
    """Extract (parsha_order, section, subsection) for sorting."""
    m = re.search(r'Tanchuma_Buber__(.+?)_(\d+)_(\d+)$', key)
    if m:
        parsha = m.group(1)
        section = int(m.group(2))
        subsection = int(m.group(3))
        order = parsha_index.get(parsha, 9999)
        return (order, section, subsection)

    return (9999, 0, 0)


def reorder_index(input_path, sort_func):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    keys = list(data.keys())
    sorted_keys = sorted(keys, key=sort_func)

    print(f"File: {input_path}")
    print(f"Total entries: {len(keys)}")
    print(f"\nFirst 15 keys BEFORE reorder:")
    for k in keys[:15]:
        print(f"  {k}")
    print(f"\nFirst 15 keys AFTER reorder:")
    for k in sorted_keys[:15]:
        print(f"  {k}")

    # Check for unknown parshas
    unknown = set()
    for k in keys:
        m = re.search(r'Tanchuma(?:_Buber)?__(.+?)_\d+_\d+$', k)
        if m:
            parsha = m.group(1)
            if parsha not in parsha_index:
                unknown.add(parsha)
    if unknown:
        print(f"\nWARNING - Unknown parshas (sorted to end): {unknown}")

    ordered = {k: data[k] for k in sorted_keys}

    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, ensure_ascii=False)

    print(f"\nDone! File rewritten with correct order.\n")


if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    print("=" * 60)
    print("Reordering Midrash_Tanchuma-index.json")
    print("=" * 60)
    reorder_index(os.path.join(base, "Midrash_Tanchuma-index.json"), sort_key_tanchuma)

    print("=" * 60)
    print("Reordering Midrash_Tanchuma_Buber-index.json")
    print("=" * 60)
    reorder_index(os.path.join(base, "Midrash_Tanchuma_Buber-index.json"), sort_key_tanchuma_buber)
