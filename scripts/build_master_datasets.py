#!/usr/bin/env python3
"""
build_master_datasets.py

The Definitive Master Build Pipeline for Thai Quran Translation Master Files.
Synthesizes and exports canonical Quran datasets in JSON, CSV, and SQLite formats:
1. Surah Metadata (114 Surahs)
2. Verses Translation (6,236 Ayahs - Clean, Annotated with Footnotes, Arabic Uthmani, English)
3. Word-by-Word WBW (83,665 Words - Arabic, Transliteration, Thai, English, Morphological Root)
4. Footnotes (7,344 Comprehensive Scholarly Annotations)
5. Tafsir Al-Mukhtasar in Thai (6,236 Ayahs)
6. Ayah Themes (1,085 Themes) & Quranic Topics (30 Topics, 5 Categories, 1,339 Verse Mappings)
7. Academic Transparency & Errata Catalog (1,656 Scholarly Revision Records)
8. Unified SQLite Database: thai_quran_master.db

Usage:
    python scripts/build_master_datasets.py
"""

import os
import sys
import csv
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
JSON_OUT_DIR = os.path.join(REPO_DIR, "json")
CSV_OUT_DIR = os.path.join(REPO_DIR, "csv")
SQLITE_OUT_DIR = os.path.join(REPO_DIR, "sqlite")
MASTER_DB_PATH = os.path.join(SQLITE_OUT_DIR, "thai_quran_master.db")

# Source Files
PARENT_DIR = os.path.dirname(REPO_DIR)
GITS_ROOT = PARENT_DIR if os.path.exists(os.path.join(PARENT_DIR, "thai-quran-app")) else r"H:\gits"

SRC_DB = os.path.join(GITS_ROOT, "thai-quran-app", "assets", "quran_offline.db")
SRC_WBW_MASTER = os.path.join(GITS_ROOT, "wbw-translation-en-th", "quran_wbw_th_en_MASTER.json")
SRC_ANNOTATED = os.path.join(GITS_ROOT, "thai_quran_translation_v4", "deliverables", "02_thai_quran_translation_v4_annotated.json")
SRC_FOOTNOTES = os.path.join(GITS_ROOT, "thai-quran-web", "src", "data", "thai_footnotes.json")
SRC_TAFSIR = os.path.join(GITS_ROOT, "thai-quran-app", "assets", "tafsir_thai_mokhtasar.json")
SRC_THEMES = os.path.join(GITS_ROOT, "thai-quran-web", "src", "data", "qul_ayah_themes.json")
SRC_TOPICS = os.path.join(GITS_ROOT, "thai-quran-web", "src", "data", "topics.json")
SRC_TRANSPARENCY = os.path.join(GITS_ROOT, "thai-quran-web", "src", "data", "transparency_errata_catalog.json")

def verify_source_files():
    sources = [
        SRC_DB, SRC_WBW_MASTER, SRC_ANNOTATED, SRC_FOOTNOTES,
        SRC_TAFSIR, SRC_THEMES, SRC_TOPICS, SRC_TRANSPARENCY
    ]
    for src in sources:
        if not os.path.exists(src):
            print(f"[ERROR] Required source file missing: {src}")
            sys.exit(1)
    print("✓ All canonical source files verified.")

def load_sources():
    print("\n--- Loading Canonical Sources ---")
    
    # 1. Database (Surahs & Uthmani text)
    conn = sqlite3.connect(SRC_DB)
    c = conn.cursor()
    c.execute("SELECT id, name_arabic, name_english, name_thai, revelation_place, verses_count, page_start FROM surahs ORDER BY id")
    surah_rows = c.fetchall()
    
    c.execute("SELECT verse_key, surah_id, verse_id, page_number, juz_number, hizb_number, text_uthmani, translation_en FROM verses ORDER BY surah_id, verse_id")
    verse_db_rows = {row[0]: row for row in c.fetchall()}

    c.execute("SELECT verse_key, position, root_arabic, part_of_speech, lemma_arabic FROM words")
    word_meta_map = {(row[0], row[1]): (row[2], row[3], row[4]) for row in c.fetchall()}
    conn.close()
    print(f"  Loaded {len(surah_rows)} surahs, {len(verse_db_rows):,} verse baselines, and {len(word_meta_map):,} word linguistic metadata.")

    # 2. Annotated Translation & Clean Translation (v4 Deliverables)
    with open(SRC_ANNOTATED, "r", encoding="utf-8") as f:
        annotated_raw = json.load(f)
    annotated_map = {item["ayah_key"]: item for item in annotated_raw}
    print(f"  Loaded {len(annotated_map):,} annotated verses from Translation v4 Deliverables.")

    # 3. Footnotes
    with open(SRC_FOOTNOTES, "r", encoding="utf-8") as f:
        footnotes_raw = json.load(f)
    print(f"  Loaded {len(footnotes_raw):,} footnote verse groups.")

    # 4. WBW Master
    with open(SRC_WBW_MASTER, "r", encoding="utf-8") as f:
        wbw_raw = json.load(f)
    print(f"  Loaded {len(wbw_raw):,} WBW verse groups.")

    # 5. Tafsir
    with open(SRC_TAFSIR, "r", encoding="utf-8") as f:
        tafsir_raw = json.load(f)
    tafsir_map = {}
    if isinstance(tafsir_raw, dict):
        for s_key, s_data in tafsir_raw.items():
            if isinstance(s_data, dict):
                for v_key, v_text in s_data.items():
                    tafsir_map[f"{s_key}:{v_key}"] = v_text
            elif isinstance(s_data, list):
                for v_idx, v_text in enumerate(s_data, 1):
                    tafsir_map[f"{s_key}:{v_idx}"] = v_text
    elif isinstance(tafsir_raw, list):
        for s_idx, s_data in enumerate(tafsir_raw, 1):
            s_num = s_data.get("surah", s_idx)
            for v_idx, v_text in enumerate(s_data.get("verses", []), 1):
                tafsir_map[f"{s_num}:{v_idx}"] = v_text
    print(f"  Loaded {len(tafsir_map):,} verse-level Tafsir entries.")

    # 6. Themes & Topics
    with open(SRC_THEMES, "r", encoding="utf-8") as f:
        themes_raw = json.load(f)
    with open(SRC_TOPICS, "r", encoding="utf-8") as f:
        topics_raw = json.load(f)
    print(f"  Loaded {len(themes_raw):,} themes and topics object.")

    # 7. Transparency Errata Catalog
    with open(SRC_TRANSPARENCY, "r", encoding="utf-8") as f:
        transparency_raw = json.load(f)
    print(f"  Loaded {len(transparency_raw):,} academic transparency errata records.")

    return surah_rows, verse_db_rows, word_meta_map, annotated_map, footnotes_raw, wbw_raw, tafsir_map, themes_raw, topics_raw, transparency_raw

def compile_master_datasets(surah_rows, verse_db_rows, word_meta_map, annotated_map, footnotes_raw, wbw_raw, tafsir_map, themes_raw, topics_raw, transparency_raw):
    print("\n--- Compiling Normalized Datasets ---")

    # 1. Surahs List
    surahs = []
    for r in surah_rows:
        surahs.append({
            "id": r[0],
            "name_ar": r[1],
            "name_en": r[2],
            "name_th": r[3],
            "revelation_place": r[4],
            "total_verses": r[5],
            "page_start": r[6]
        })

    # 2. Verses List
    verses = []
    tafsir_list = []
    for s in surahs:
        s_id = s["id"]
        for v_id in range(1, s["total_verses"] + 1):
            vk = f"{s_id}:{v_id}"
            db_row = verse_db_rows.get(vk)
            ann_row = annotated_map.get(vk, {})
            
            clean_th = ann_row.get("translation_clean") or ""
            annotated_th = ann_row.get("translation_annotated") or clean_th
            t_text = tafsir_map.get(vk, "")
            
            verses.append({
                "verse_key": vk,
                "surah_id": s_id,
                "verse_id": v_id,
                "page": db_row[3] if db_row else 1,
                "juz": db_row[4] if db_row else 1,
                "hizb": db_row[5] if db_row else 1,
                "arabic_uthmani": db_row[6] if db_row else "",
                "translation_th": clean_th,
                "translation_annotated_th": annotated_th,
                "translation_en": db_row[7] if db_row else "",
                "tafsir_th": t_text
            })

            if t_text:
                tafsir_list.append({
                    "verse_key": vk,
                    "surah_id": s_id,
                    "verse_id": v_id,
                    "text": t_text
                })

    # 3. Footnotes Flat List
    footnotes = []
    fn_counter = 1
    for vk, v_fn_data in footnotes_raw.items():
        s_id, v_id = map(int, vk.split(":"))
        fn_list = v_fn_data.get("footnotes", [])
        for fn in fn_list:
            footnotes.append({
                "id": fn_counter,
                "verse_key": vk,
                "surah_id": s_id,
                "verse_id": v_id,
                "footnote_marker": fn.get("id"),
                "orig_id": fn.get("origId") or fn.get("orig_id"),
                "text": fn.get("text", "").strip()
            })
            fn_counter += 1

    # 4. Words (WBW) Flat List
    words = []
    w_counter = 1
    for v in wbw_raw:
        vk = v.get("verse_key", "")
        s_id, v_id = map(int, vk.split(":"))
        for w in v.get("words", []):
            pos = w.get("position", 1)
            meta = word_meta_map.get((vk, pos), ("", "", ""))
            words.append({
                "id": w_counter,
                "verse_key": vk,
                "surah_id": s_id,
                "verse_id": v_id,
                "position": pos,
                "arabic": w.get("arabic", ""),
                "transliteration": w.get("transliteration", ""),
                "translation_th": w.get("thai", ""),
                "translation_en": w.get("english", ""),
                "root_arabic": meta[0],
                "part_of_speech": meta[1],
                "lemma_arabic": meta[2]
            })
            w_counter += 1

    # 5. Transparency Errata Catalog Flat List
    transparency = []
    for idx, item in enumerate(transparency_raw, 1):
        ayah = str(item.get("ayah", "")).strip()
        s_id, v_id = map(int, ayah.split(":")) if ":" in ayah else (0, 0)
        transparency.append({
            "id": idx,
            "verse_key": ayah,
            "surah_id": s_id,
            "verse_id": v_id,
            "type": item.get("type", "GENERAL"),
            "target": item.get("target", ""),
            "replacement": item.get("replacement", ""),
            "reason": item.get("reason", ""),
            "source": item.get("source", ""),
            "missing_from_printed_copy": 1 if item.get("missingFromPrintedCopy") else 0
        })

    print(f"✓ Compiled {len(surahs)} surahs, {len(verses):,} verses, {len(footnotes):,} footnotes, {len(words):,} words, and {len(transparency):,} transparency records.")
    return surahs, verses, footnotes, words, tafsir_list, themes_raw, topics_raw, transparency

def export_json_files(surahs, verses, footnotes, words, tafsir_list, themes, topics, transparency):
    print("\n--- Exporting JSON Datasets ---")
    os.makedirs(JSON_OUT_DIR, exist_ok=True)

    json_files = {
        "surahs.json": surahs,
        "quran_thai_translation.json": verses,
        "quran_footnotes.json": footnotes,
        "quran_wbw_th_en.json": words,
        "quran_tafsir_mokhtasar.json": tafsir_list,
        "quran_themes.json": themes,
        "quran_topics.json": topics,
        "quran_transparency_catalog.json": transparency
    }

    for fname, data in json_files.items():
        out_path = os.path.join(JSON_OUT_DIR, fname)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(f"  -> Exported {fname:32s} ({size_mb:5.2f} MB)")

def export_csv_files(surahs, verses, footnotes, transparency):
    print("\n--- Exporting CSV Datasets (Excel & Data Science Ready) ---")
    os.makedirs(CSV_OUT_DIR, exist_ok=True)

    # 1. Transparency Errata CSV (UTF-8 with BOM for seamless Excel compatibility)
    transparency_csv = os.path.join(CSV_OUT_DIR, "quran_transparency_catalog.csv")
    with open(transparency_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "verse_key", "surah_id", "verse_id", "type",
            "target", "replacement", "reason", "source", "missing_from_printed_copy"
        ])
        writer.writeheader()
        writer.writerows(transparency)
    size_mb = os.path.getsize(transparency_csv) / (1024 * 1024)
    print(f"  -> Exported quran_transparency_catalog.csv   ({size_mb:5.2f} MB)")

    # 2. Surahs CSV
    surahs_csv = os.path.join(CSV_OUT_DIR, "surahs.csv")
    with open(surahs_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "name_ar", "name_en", "name_th", "revelation_place", "total_verses", "page_start"
        ])
        writer.writeheader()
        writer.writerows(surahs)
    print(f"  -> Exported surahs.csv                      ({os.path.getsize(surahs_csv)/1024:5.2f} KB)")

    # 3. Verses Translation CSV
    verses_csv = os.path.join(CSV_OUT_DIR, "quran_thai_translation.csv")
    with open(verses_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "verse_key", "surah_id", "verse_id", "page", "juz", "hizb",
            "arabic_uthmani", "translation_th", "translation_annotated_th", "translation_en"
        ], extrasaction='ignore')
        writer.writeheader()
        writer.writerows(verses)
    size_mb = os.path.getsize(verses_csv) / (1024 * 1024)
    print(f"  -> Exported quran_thai_translation.csv      ({size_mb:5.2f} MB)")

def build_sqlite_database(surahs, verses, footnotes, words, tafsir_list, themes, topics, transparency):
    print("\n--- Building Master SQLite Database ---")
    os.makedirs(SQLITE_OUT_DIR, exist_ok=True)
    if os.path.exists(MASTER_DB_PATH):
        os.remove(MASTER_DB_PATH)

    conn = sqlite3.connect(MASTER_DB_PATH)
    c = conn.cursor()

    # Enable pragmas for speed and integrity
    c.execute("PRAGMA synchronous = OFF")
    c.execute("PRAGMA journal_mode = MEMORY")

    # 1. Metadata Table
    c.execute("""
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    meta_entries = [
        ("title", "Canonical Master Dataset for Thai Quran Translation"),
        ("version", "4.0.0"),
        ("standardization_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        ("orthography_standard", "MASTER_SPELLING_STANDARDIZATION_PLAN.md"),
        ("total_surahs", str(len(surahs))),
        ("total_verses", str(len(verses))),
        ("total_words", str(len(words))),
        ("total_footnotes", str(len(footnotes))),
        ("total_tafsir", str(len(tafsir_list))),
        ("total_themes", str(len(themes))),
        ("total_transparency_records", str(len(transparency)))
    ]
    c.executemany("INSERT INTO metadata VALUES (?, ?)", meta_entries)

    # 2. Surahs Table
    c.execute("""
        CREATE TABLE surahs (
            id INTEGER PRIMARY KEY,
            name_ar TEXT NOT NULL,
            name_en TEXT NOT NULL,
            name_th TEXT NOT NULL,
            revelation_place TEXT NOT NULL,
            total_verses INTEGER NOT NULL,
            page_start INTEGER NOT NULL
        )
    """)
    c.executemany("""
        INSERT INTO surahs VALUES (:id, :name_ar, :name_en, :name_th, :revelation_place, :total_verses, :page_start)
    """, surahs)

    # 3. Verses Table
    c.execute("""
        CREATE TABLE verses (
            verse_key TEXT PRIMARY KEY,
            surah_id INTEGER NOT NULL,
            verse_id INTEGER NOT NULL,
            page INTEGER NOT NULL,
            juz INTEGER NOT NULL,
            hizb INTEGER NOT NULL,
            arabic_uthmani TEXT NOT NULL,
            translation_th TEXT NOT NULL,
            translation_annotated_th TEXT NOT NULL,
            translation_en TEXT NOT NULL,
            tafsir_th TEXT,
            FOREIGN KEY (surah_id) REFERENCES surahs(id)
        )
    """)
    c.executemany("""
        INSERT INTO verses VALUES (
            :verse_key, :surah_id, :verse_id, :page, :juz, :hizb,
            :arabic_uthmani, :translation_th, :translation_annotated_th,
            :translation_en, :tafsir_th
        )
    """, verses)

    # 4. Footnotes Table
    c.execute("""
        CREATE TABLE footnotes (
            id INTEGER PRIMARY KEY,
            verse_key TEXT NOT NULL,
            surah_id INTEGER NOT NULL,
            verse_id INTEGER NOT NULL,
            footnote_marker INTEGER,
            orig_id TEXT,
            text TEXT NOT NULL,
            FOREIGN KEY (verse_key) REFERENCES verses(verse_key)
        )
    """)
    c.executemany("""
        INSERT INTO footnotes VALUES (
            :id, :verse_key, :surah_id, :verse_id, :footnote_marker, :orig_id, :text
        )
    """, footnotes)

    # 5. Words (WBW) Table
    c.execute("""
        CREATE TABLE words (
            id INTEGER PRIMARY KEY,
            verse_key TEXT NOT NULL,
            surah_id INTEGER NOT NULL,
            verse_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            arabic TEXT NOT NULL,
            transliteration TEXT,
            translation_th TEXT NOT NULL,
            translation_en TEXT,
            root_arabic TEXT,
            part_of_speech TEXT,
            lemma_arabic TEXT,
            FOREIGN KEY (verse_key) REFERENCES verses(verse_key)
        )
    """)
    c.executemany("""
        INSERT INTO words VALUES (
            :id, :verse_key, :surah_id, :verse_id, :position, :arabic,
            :transliteration, :translation_th, :translation_en,
            :root_arabic, :part_of_speech, :lemma_arabic
        )
    """, words)

    # 6. Tafsir Table
    c.execute("""
        CREATE TABLE tafsir (
            verse_key TEXT PRIMARY KEY,
            surah_id INTEGER NOT NULL,
            verse_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (verse_key) REFERENCES verses(verse_key)
        )
    """)
    c.executemany("""
        INSERT INTO tafsir VALUES (:verse_key, :surah_id, :verse_id, :text)
    """, tafsir_list)

    # 7. Themes Table
    c.execute("""
        CREATE TABLE themes (
            id INTEGER PRIMARY KEY,
            surah_id INTEGER NOT NULL,
            ayah_from INTEGER NOT NULL,
            ayah_to INTEGER NOT NULL,
            total_ayahs INTEGER NOT NULL,
            title_th TEXT,
            title_en TEXT,
            theme_th TEXT,
            theme_en TEXT
        )
    """)
    theme_rows = []
    for t in themes:
        theme_rows.append((
            t.get("id"),
            t.get("surah"),
            t.get("ayah_from"),
            t.get("ayah_to"),
            t.get("total_ayahs"),
            t.get("title_th"),
            t.get("title_en"),
            t.get("theme_th"),
            t.get("theme_en")
        ))
    c.executemany("INSERT INTO themes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", theme_rows)

    # 8. Topic Categories, Topics, and Topic Verses
    c.execute("""
        CREATE TABLE topic_categories (
            id INTEGER PRIMARY KEY,
            title_th TEXT NOT NULL,
            title_en TEXT NOT NULL,
            icon_name TEXT,
            sort_order INTEGER
        )
    """)
    categories = topics.get("categories", [])
    cat_rows = [(cat["id"], cat["title_th"], cat["title_en"], cat.get("icon_name"), cat.get("sort_order")) for cat in categories]
    c.executemany("INSERT INTO topic_categories VALUES (?, ?, ?, ?, ?)", cat_rows)

    c.execute("""
        CREATE TABLE topics (
            id INTEGER PRIMARY KEY,
            category_id INTEGER NOT NULL,
            title_th TEXT NOT NULL,
            title_en TEXT NOT NULL,
            verses_count INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES topic_categories(id)
        )
    """)
    topic_items = topics.get("topics", [])
    top_rows = [(t["id"], t["category_id"], t["title_th"], t["title_en"], t["verses_count"]) for t in topic_items]
    c.executemany("INSERT INTO topics VALUES (?, ?, ?, ?, ?)", top_rows)

    c.execute("""
        CREATE TABLE topic_verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            verse_key TEXT NOT NULL,
            FOREIGN KEY (topic_id) REFERENCES topics(id),
            FOREIGN KEY (verse_key) REFERENCES verses(verse_key)
        )
    """)
    verse_mappings = topics.get("topic_verses", {})
    tv_rows = []
    for top_id_str, vk_list in verse_mappings.items():
        top_id = int(top_id_str)
        for vk in vk_list:
            tv_rows.append((top_id, vk))
    c.executemany("INSERT INTO topic_verses (topic_id, verse_key) VALUES (?, ?)", tv_rows)

    # 9. Academic Transparency & Errata Catalog Table
    c.execute("""
        CREATE TABLE transparency_catalog (
            id INTEGER PRIMARY KEY,
            verse_key TEXT NOT NULL,
            surah_id INTEGER NOT NULL,
            verse_id INTEGER NOT NULL,
            errata_type TEXT NOT NULL,
            target TEXT NOT NULL,
            replacement TEXT NOT NULL,
            reason TEXT NOT NULL,
            source TEXT NOT NULL,
            missing_from_printed_copy INTEGER DEFAULT 0,
            FOREIGN KEY (verse_key) REFERENCES verses(verse_key)
        )
    """)
    c.executemany("""
        INSERT INTO transparency_catalog VALUES (
            :id, :verse_key, :surah_id, :verse_id, :type,
            :target, :replacement, :reason, :source, :missing_from_printed_copy
        )
    """, transparency)

    # 10. Create Performance Indexes
    print("  Creating relational indexes...")
    c.execute("CREATE INDEX idx_verses_surah_ayah ON verses(surah_id, verse_id)")
    c.execute("CREATE INDEX idx_verses_page ON verses(page)")
    c.execute("CREATE INDEX idx_verses_juz ON verses(juz)")
    c.execute("CREATE INDEX idx_footnotes_vk ON footnotes(verse_key)")
    c.execute("CREATE INDEX idx_words_vk_pos ON words(verse_key, position)")
    c.execute("CREATE INDEX idx_words_root ON words(root_arabic)")
    c.execute("CREATE INDEX idx_tafsir_surah ON tafsir(surah_id)")
    c.execute("CREATE INDEX idx_themes_surah ON themes(surah_id)")
    c.execute("CREATE INDEX idx_topic_verses_topic ON topic_verses(topic_id)")
    c.execute("CREATE INDEX idx_topic_verses_vk ON topic_verses(verse_key)")
    c.execute("CREATE INDEX idx_transparency_vk ON transparency_catalog(verse_key)")
    c.execute("CREATE INDEX idx_transparency_type ON transparency_catalog(errata_type)")

    conn.commit()
    c.execute("VACUUM")
    conn.close()

    db_size_mb = os.path.getsize(MASTER_DB_PATH) / (1024 * 1024)
    print(f"✓ Master SQLite Database built successfully at {MASTER_DB_PATH} ({db_size_mb:5.2f} MB)")

def main():
    print("=" * 80)
    print("THAI QURAN TRANSLATION MASTER DATASET BUILDER")
    print("=" * 80)

    verify_source_files()
    sources = load_sources()
    datasets = compile_master_datasets(*sources)
    export_json_files(*datasets)
    export_csv_files(datasets[0], datasets[1], datasets[2], datasets[7])
    build_sqlite_database(*datasets)

    print("\n" + "=" * 80)
    print("MASTER DATASETS BUILD COMPLETE & READY FOR PRODUCTION!")
    print("=" * 80)

if __name__ == "__main__":
    main()
