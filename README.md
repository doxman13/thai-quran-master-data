# Thai Quran Translation Master Dataset
### ฐานข้อมูลพระมหาคัมภีร์อัลกุรอานฉบับแปลภาษาไทย มาตรฐานสากลครบวงจร (JSON & SQLite)

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![SQLite Version](https://img.shields.io/badge/SQLite-3-blue.svg)](https://www.sqlite.org/)
[![Total Verses](https://img.shields.io/badge/Verses-6%2C236-green.svg)](#)
[![Total Words](https://img.shields.io/badge/Words-83%2C665-orange.svg)](#)
[![Total Footnotes](https://img.shields.io/badge/Footnotes-7%2C337-purple.svg)](#)

---

## 1. บทนำ (Introduction)

คลังข้อมูลชุดนี้เป็น **"ฐานข้อมูลแม่บทฉบับสมบูรณ์ (Canonical Master Dataset)"** สำหรับการศึกษา ค้นคว้า และพัฒนาแอปพลิเคชันอัลกุรอานภาษาไทย โดยรวบรวมเนื้อหาครบทั้ง 5 เสาหลัก ผ่านการจัดมาตรฐานอักขรวิธีคำทับศัพท์และศัพท์ศาสนบัญญัติ (Orthography Standardization) 100% ตรงตามหลักภาษาศาสตร์และจารีตอิสลาม

จัดเก็บใน 2 รูปแบบมาตรฐานสากล:
- **`sqlite/thai_quran_master.db`**: ฐานข้อมูลเชิงสัมพันธ์ (Relational Database) ไฟล์เดียวที่เชื่อมโยงตารางอย่างสมบูรณ์ พร้อมดัชนี (Indexes) ความเร็วสูง
- **`json/*.json`**: ชุดข้อมูล JSON มาตรฐาน แยกตามประเภท สะดวกต่อการนำไปใช้งานใน Web, Mobile, API, หรือ Data Science Pipeline

---

## 2. โครงสร้างข้อมูล 5 เสาหลัก (The 5 Pillars)

```mermaid
graph TD
    M["thai-quran-master-data"] --> S["1. ซูเราะฮฺ (114 Surahs)"]
    M --> V["2. ตัวบทและคำแปล (6,236 Verses)"]
    M --> F["3. เชิงอรรถอธิบาย (7,337 Footnotes)"]
    M --> W["4. คำต่อคำ WBW (83,665 Words)"]
    M --> T["5. ตัฟซีรย่อ (6,236 Tafsir)"]
    M --> TH["6. หัวข้อและธีม (Themes & Topics)"]

    V --> V1["ภาษาอาหรับอุษมานีย์ (Uthmani)"]
    V --> V2["คำแปลภาษาไทยตัวเต็ม (Clean)"]
    V --> V3["คำแปลภาษาไทยกำกับเชิงอรรถ (Annotated)"]
    V --> V4["คำแปลภาษาอังกฤษ (Sahih Int.)"]
```

1. **พระมหาคัมภีร์ (6,236 โองการ):**
   - อาหรับมุศฮัฟมะดีนะฮฺ (Uthmani Script)
   - คำแปลภาษาไทยฉบับมาตรฐานสมาคมนักเรียนเก่าอาหรับฯ (King Fahd Edition v4 Standard)
   - ฉบับกำกับหมายเลขเชิงอรรถ (`[1]`, `[2]`) และฉบับคลีน
   - หมายเลขหน้ามุศฮัฟ (604 หน้า), ญุซอ์ (30 ญุซอ์), และฮิซบ์ (240 ฮิซบ์)
2. **คำแปลคำต่อคำ (Word-by-Word WBW — 83,665 คำ):**
   - แยกคำ 1-to-1 สอดคล้องกับรากศัพท์ภาษาอาหรับคลาสสิก (Classical Arabic Root)
   - คำทับศัพท์สัทอักษร (Phonetic Transliteration)
   - คำแปลภาษาไทยและภาษาอังกฤษประจำตำแหน่งคำ
   - รากศัพท์ภาษาอาหรับ (جذر الكلمة), ประเภทคำ (POS), และ Lemma
3. **เชิงอรรถวิชาการ (7,337 รายการ):**
   - คำอธิบายบริบทการประทานโองการ ประวัติศาสตร์ และขยายความหมายอย่างละเอียด
4. **ตัฟซีรมุคตะศ็อรภาษาไทย (Tafsir Al-Mukhtasar — 6,236 โองการ):**
   - คำอธิบายความหมายสรุปย่อรายโองการจากศูนย์ตัฟซีร ณ นครมักกะฮฺ
5. **หัวข้อและธีมเนื้อหา (Themes & Topics):**
   - สรุปใจความสำคัญของกลุ่มโองการ 1,085 ช่วง (Ayah Themes)
   - ดัชนีจำแนกตามประเด็นเนื้อหา 30 หัวข้อ ครอบคลุม 1,339 โองการ

---

## 3. ผังโครงสร้างไดเรกทอรี (Directory Layout)

```
thai-quran-master-data/
├── README.md                           # คู่มือการใช้งานและภาพรวม
├── SCHEMA.md                           # รายละเอียดสคีมาของ SQLite และ JSON
├── json/                               # ชุดข้อมูล JSON มาตรฐาน
│   ├── surahs.json                     # ข้อมูลซูเราะฮฺทั้ง 114 บท
│   ├── quran_thai_translation.json     # ตัวบทอาหรับและคำแปล 6,236 โองการ
│   ├── quran_footnotes.json            # เชิงอรรถอธิบาย 7,337 ข้อ
│   ├── quran_wbw_th_en.json            # คำแปลคำต่อคำ 83,665 คำ
│   ├── quran_tafsir_mokhtasar.json     # ตัฟซีรย่อภาษาไทย 6,236 โองการ
│   ├── quran_themes.json               # ธีมเนื้อหา 1,085 ช่วง
│   └── quran_topics.json               # หมวดหมู่และดัชนี 30 หัวข้อ
├── sqlite/                             # ฐานข้อมูล SQLite มาตรฐาน
│   └── thai_quran_master.db            # ไฟล์ SQLite รวมทุกตาราง (39.7 MB)
└── scripts/                            # สคริปต์ไปป์ไลน์
    ├── build_master_datasets.py        # สคริปต์สังเคราะห์ข้อมูลต้นทาง
    └── verify_master_datasets.py       # สคริปต์ตรวจความถูกต้อง 100%
```

---

## 4. ตัวอย่างการดึงข้อมูล (Usage & Examples)

### 4.1 การคิวรีด้วย SQLite (Python)

```python
import sqlite3

conn = sqlite3.connect("sqlite/thai_quran_master.db")
c = conn.cursor()

# 1. ค้นหาคำแปลและเชิงอรรถของโองการ 1:4
query = """
    SELECT v.verse_key, v.arabic_uthmani, v.translation_annotated_th, f.text AS footnote
    FROM verses v
    LEFT JOIN footnotes f ON v.verse_key = f.verse_key
    WHERE v.verse_key = '1:4'
"""
c.execute(query)
row = c.fetchone()
print(f"[{row[0]}] {row[1]}")
print(f"คำแปล: {row[2]}")
print(f"เชิงอรรถ: {row[3]}")

# 2. ดึงคำแปลคำต่อคำ (WBW) ของโองการ 1:1
c.execute("""
    SELECT position, arabic, transliteration, translation_th
    FROM words
    WHERE verse_key = '1:1'
    ORDER BY position
""")
for pos, ar, tr, th in c.fetchall():
    print(f"คำที่ {pos}: {ar} ({tr}) = {th}")

conn.close()
```

### 4.2 การอ่านข้อมูล JSON (Node.js / TypeScript)

```typescript
import * as fs from 'fs';

// อ่านคำแปลพระมหาคัมภีร์
const verses = JSON.parse(fs.readFileSync('json/quran_thai_translation.json', 'utf-8'));
const ayah1_1 = verses.find((v: any) => v.verse_key === '1:1');
console.log(ayah1_1.arabic_uthmani);
console.log(ayah1_1.translation_th);
```

---

## 5. การตรวจสอบความสมบูรณ์ของข้อมูล (Integrity Verification)

ท่านสามารถรันชุดทดสอบเพื่อตรวจสอบความสมบูรณ์ของโครงสร้างข้อมูล ดัชนี และจำนวนแถวทุกตารางได้ตลอดเวลา:

```bash
python scripts/verify_master_datasets.py
```

ผลลัพธ์การตรวจสอบมาตรฐาน:
- **Database Integrity:** `PRAGMA integrity_check = ok`
- **Total Surahs:** 114 บท
- **Total Verses:** 6,236 โองการ
- **Total Words:** 83,665 คำ (WBW)
- **Total Footnotes:** 7,337 รายการ
- **Total Tafsir:** 6,236 โองการ
- **Total Themes:** 1,085 ช่วง

---

## 6. ลิขสิทธิ์และการอ้างอิง (License & Attribution)

- **ตัวบทพระมหาคัมภีร์อัลกุรอานภาษาอาหรับ:** ศูนย์กษัตริย์ฟะฮัดเพื่อการพิมพ์อัลกุรอาน (King Fahd Glorious Quran Printing Complex, Madinah)
- **คำแปลพระมหาคัมภีร์ภาษาไทยและเชิงอรรถ:** สมาคมนักเรียนเก่าอาหรับ ประเทศไทย / ศูนย์กษัตริย์ฟะฮัดฯ
- **ชุดข้อมูลและการจัดระเบียบโครงสร้าง:** เผยแพร่ภายใต้สัญญาอนุญาต [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)
