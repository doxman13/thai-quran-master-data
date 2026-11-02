#!/usr/bin/env python3
"""
verify_master_datasets.py

Comprehensive Integrity & Verification Suite for Thai Quran Master Datasets.
Validates:
1. SQLite Database integrity and table row counts (including transparency_catalog).
2. JSON files presence, parsing, and item count alignment.
3. CSV files presence, encoding (UTF-8 with BOM), and row counts.
4. Sample complex SQL queries (surah join, WBW word lookups, footnotes, transparency).
"""

import os
import sys
import csv
import json
import sqlite3

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DB_PATH = os.path.join(REPO_DIR, "sqlite", "thai_quran_master.db")
JSON_DIR = os.path.join(REPO_DIR, "json")
CSV_DIR = os.path.join(REPO_DIR, "csv")

EXPECTED_COUNTS = {
    "surahs": 114,
    "verses": 6236,
    "footnotes": 7342,
    "words": 83665,
    "tafsir": 6236,
    "themes": 1085,
    "topic_categories": 5,
    "topics": 30,
    "topic_verses": 1339,
    "transparency_catalog": 1655
}

def verify_sqlite():
    print("=" * 80)
    print("1. SQLITE MASTER DATABASE INTEGRITY & METRICS")
    print("=" * 80)
    if not os.path.exists(DB_PATH):
        print(f"[FAIL] SQLite database not found at {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Integrity Check
    c.execute("PRAGMA integrity_check")
    res = c.fetchone()[0]
    print(f"PRAGMA integrity_check: {res}")
    if res != "ok":
        print("[FAIL] Database integrity check failed!")
        return False

    # Check Metadata
    c.execute("SELECT key, value FROM metadata")
    print("\nDatabase Metadata:")
    for k, v in c.fetchall():
        print(f"  {k:28s}: {v}")

    # Check Table Counts
    print("\nTable Row Counts:")
    all_ok = True
    for table_name, expected in EXPECTED_COUNTS.items():
        c.execute(f"SELECT COUNT(*) FROM {table_name}")
        actual = c.fetchone()[0]
        status = "✓ OK" if actual == expected else f"✗ MISMATCH (expected {expected})"
        print(f"  {table_name:22s}: {actual:6,d} rows  [{status}]")
        if actual != expected:
            all_ok = False

    # Sample Verification Query
    print("\nSample Relational Join (Surah 1: Al-Fatihah, Verse 1:4):")
    query = """
        SELECT v.verse_key, v.arabic_uthmani, v.translation_th, v.translation_annotated_th, f.text AS footnote
        FROM verses v
        LEFT JOIN footnotes f ON v.verse_key = f.verse_key
        WHERE v.verse_key = '1:4'
    """
    c.execute(query)
    for r in c.fetchall():
        print(f"  Verse Key : {r[0]}")
        print(f"  Arabic    : {r[1]}")
        print(f"  Thai Clean: {r[2]}")
        print(f"  Annotated : {r[3]}")
        print(f"  Footnote  : {r[4]}")

    print("\nSample WBW Query (Surah 1:1 Words):")
    c.execute("SELECT position, arabic, transliteration, translation_th FROM words WHERE verse_key = '1:1' ORDER BY position")
    for r in c.fetchall():
        print(f"  Word #{r[0]}: {r[1]:15s} ({r[2]:12s}) -> {r[3]}")

    print("\nSample Academic Transparency Query (Surah 2:1 Errata Record):")
    c.execute("SELECT verse_key, errata_type, target, replacement, reason, source FROM transparency_catalog WHERE verse_key = '2:1' LIMIT 1")
    tr = c.fetchone()
    if tr:
        print(f"  Ayah       : {tr[0]}")
        print(f"  Type       : {tr[1]}")
        print(f"  Target     : {tr[2]}")
        print(f"  Replacement: {tr[3]}")
        print(f"  Reason     : {tr[4]}")
        print(f"  Source     : {tr[5]}")

    conn.close()
    return all_ok

def verify_json():
    print("\n" + "=" * 80)
    print("2. JSON DATASETS INTEGRITY & PARSING")
    print("=" * 80)

    json_files = {
        "surahs.json": 114,
        "quran_thai_translation.json": 6236,
        "quran_footnotes.json": 7342,
        "quran_wbw_th_en.json": 83665,
        "quran_tafsir_mokhtasar.json": 6236,
        "quran_themes.json": 1085,
        "quran_transparency_catalog.json": 1655,
        "quran_topics.json": None  # Object with categories/topics/mappings
    }

    all_ok = True
    for fname, expected_count in json_files.items():
        fpath = os.path.join(JSON_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  {fname:32s}: [MISSING]")
            all_ok = False
            continue

        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if expected_count is not None:
            actual = len(data)
            status = "✓ OK" if actual == expected_count else f"✗ MISMATCH (expected {expected_count})"
            print(f"  {fname:32s}: {actual:6,d} items ({size_mb:5.2f} MB)  [{status}]")
            if actual != expected_count:
                all_ok = False
        else:
            cat_len = len(data.get("categories", []))
            top_len = len(data.get("topics", []))
            print(f"  {fname:32s}: {cat_len} categories, {top_len} topics ({size_mb:5.2f} MB)  [✓ OK]")

    return all_ok

def verify_csv():
    print("\n" + "=" * 80)
    print("3. CSV DATASETS INTEGRITY & ENCODING")
    print("=" * 80)

    csv_files = {
        "surahs.csv": 114,
        "quran_thai_translation.csv": 6236,
        "quran_transparency_catalog.csv": 1655
    }

    all_ok = True
    for fname, expected_count in csv_files.items():
        fpath = os.path.join(CSV_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  {fname:32s}: [MISSING]")
            all_ok = False
            continue

        with open(fpath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
            actual = len(rows)

        status = "✓ OK" if actual == expected_count else f"✗ MISMATCH (expected {expected_count})"
        size_kb = os.path.getsize(fpath) / 1024
        print(f"  {fname:32s}: {actual:6,d} rows ({size_kb:6.1f} KB)  [{status}]")
        if actual != expected_count:
            all_ok = False

    return all_ok

def main():
    db_ok = verify_sqlite()
    json_ok = verify_json()
    csv_ok = verify_csv()

    print("\n" + "=" * 80)
    if db_ok and json_ok and csv_ok:
        print("ALL MASTER DATASET VERIFICATION CHECKS PASSED (100% INTEGRITY)!")
    else:
        print("SOME CHECKS FAILED - PLEASE REVIEW LOGS ABOVE.")
        sys.exit(1)
    print("=" * 80)

if __name__ == "__main__":
    main()
