"""
reorder_sefaria.py — סידור אינדקסי תנחומא ותנחומא בובר בדיוק לפי סדר ספריא.
כולל טיפול בקטעי נספח (Appendix) עבור תנחומא בובר.
כתיבה בפורמט JSON קומפקטי תואם build_index.py.

שימוש:
    python reorder_sefaria.py                     # עובד על התיקייה הנוכחית
    python reorder_sefaria.py <תיקיית-נתונים>     # תיקייה ספציפית
"""
import json
import re
import sys
import os

# ═══════════════════════════════════════════
# Sefaria parsha order (from Sefaria API)
# ═══════════════════════════════════════════

TANCHUMA_SEFARIA_ORDER = [
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
    "VZot_HaBerachah",
]

BUBER_SEFARIA_ORDER = [
    "Bereshit", "Noach", "Lech_Lecha", "Vayera", "Chayei_Sara",
    "Toldot", "Vayetzei", "Vayishlach", "Vayeshev", "Miketz",
    "Vayigash", "Vayechi",
    "Shemot", "Vaera", "Bo", "Beshalach", "Yitro",
    "Mishpatim", "Terumah", "Tetzaveh", "Ki_Tisa", "Vayakhel", "Pekudei",
    "Vayikra", "Tzav", "Shmini", "Tazria", "Metzora",
    "Achrei_Mot", "Kedoshim", "Emor", "Behar", "Bechukotai",
    "Bamidbar", "Nasso", "Behaalotcha",
    "Shlach", "Appendix_to_Shlach",
    "Korach", "Appendix_to_Korach",
    "Chukat", "Appendix_to_Chukat",
    "Balak", "Pinchas", "Matot", "Masei",
    "Devarim", "Appendix_to_Devarim",
    "Vaetchanan", "Appendix_to_Vaetchanan",
    "Eikev",
    "Reeh", "Appendix_to_Reeh",
    "Shoftim", "Ki_Teitzei", "Ki_Tavo", "Nitzavim",
    "HaAzinu", "VZot_HaBerachah",
]


def build_sort_key(parsha_order):
    lookup = {}
    for i, p in enumerate(parsha_order):
        lookup[p] = i
    return lookup


def extract_parsha_and_nums_tanchuma(key):
    m = re.search(r'Otzar_Midrashim__Midrash_Tanchuma_(\d+)$', key)
    if m:
        return ('__OTZAR__', int(m.group(1)), 0)
    m = re.search(r'Midrash_Tanchuma__(.+?)_(\d+)_(\d+)$', key)
    if m:
        return (m.group(1), int(m.group(2)), int(m.group(3)))
    return ('__UNKNOWN__', 0, 0)


def extract_parsha_and_nums_buber(key):
    m = re.search(r'Tanchuma_Buber__(.+?)_(\d+)_(\d+)$', key)
    if m:
        return (m.group(1), int(m.group(2)), int(m.group(3)))
    return ('__UNKNOWN__', 0, 0)


def reorder_tanchuma(idx_path, parsha_order, extract_func):
    with open(idx_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lookup = build_sort_key(parsha_order)

    def sort_key(key):
        parsha, sec, subsec = extract_func(key)
        if parsha == '__OTZAR__':
            return (-1, 0, sec, subsec)
        order = lookup.get(parsha, 9999)
        if order == 9999:
            print(f"  WARNING: Unknown parsha '{parsha}' in key '{key}'")
        return (0, order, sec, subsec)

    sorted_keys = sorted(data.keys(), key=sort_key)
    ordered = {k: data[k] for k in sorted_keys}

    with open(idx_path, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, ensure_ascii=False, separators=(',', ':'))

    return sorted_keys


if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    # ═══ Tanchuma ═══
    print("=" * 60)
    print("Reordering Midrash_Tanchuma-index.json (Sefaria order)")
    print("=" * 60)

    tanchuma_path = os.path.join(base, "Midrash_Tanchuma-index.json")
    keys = reorder_tanchuma(tanchuma_path, TANCHUMA_SEFARIA_ORDER, extract_parsha_and_nums_tanchuma)

    parshas = []
    for k in keys:
        p, _, _ = extract_parsha_and_nums_tanchuma(k)
        if not parshas or parshas[-1] != p:
            parshas.append(p)
    print(f"  Total entries: {len(keys)}")
    print(f"  Parsha order:")
    for i, p in enumerate(parshas):
        print(f"    {i+1}. {p}")

    # ═══ Tanchuma Buber ═══
    print("\n" + "=" * 60)
    print("Reordering Midrash_Tanchuma_Buber-index.json (Sefaria order)")
    print("=" * 60)

    buber_path = os.path.join(base, "Midrash_Tanchuma_Buber-index.json")
    keys = reorder_tanchuma(buber_path, BUBER_SEFARIA_ORDER, extract_parsha_and_nums_buber)

    parshas = []
    for k in keys:
        p, _, _ = extract_parsha_and_nums_buber(k)
        if not parshas or parshas[-1] != p:
            parshas.append(p)
    print(f"  Total entries: {len(keys)}")
    print(f"  Parsha order:")
    for i, p in enumerate(parshas):
        print(f"    {i+1}. {p}")

    print("\nDone!")
