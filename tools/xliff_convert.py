#!/usr/bin/env python3
"""
Outer Wilds CHT Translation converter
1. Translation.txt → XLIFF 1.2  (for memoQ)
2. XLIFF 1.2 → Translation.txt  (rebuild after editing)
"""

import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

XLIFF_NS = 'urn:oasis:names:tc:xliff:document:1.2'


# ── Mode 1: Translation.txt → XLIFF ──────────────────────────────────────────

def translation_to_xliff(src_path: str, dst_path: str):
    tree = ET.parse(src_path)
    root = tree.getroot()

    xliff = ET.Element('xliff', {
        'version': '1.2',
        'xmlns': XLIFF_NS,
    })
    file_el = ET.SubElement(xliff, 'file', {
        'original': 'translation.txt',
        'source-language': 'en',
        'target-language': 'zh-TW',
        'datatype': 'xml',
    })
    body = ET.SubElement(file_el, 'body')

    uid = [1]  # mutable for nested function

    def add_unit(key_el, val_el, note_text):
        tu = ET.SubElement(body, 'trans-unit', {'id': str(uid[0])})
        ET.SubElement(tu, 'source').text = (key_el.text or '').strip()
        ET.SubElement(tu, 'target').text = (val_el.text or '').strip()
        ET.SubElement(tu, 'note').text = note_text
        uid[0] += 1

    # Section 1: <entry>
    for entry in root.findall('entry'):
        k, v = entry.find('key'), entry.find('value')
        if k is not None and v is not None:
            add_unit(k, v, 'entry')

    # Section 2: <table_shipLog>
    shiplog = root.find('table_shipLog')
    if shiplog is not None:
        for entry in shiplog.findall('TranslationTableEntry'):
            k, v = entry.find('key'), entry.find('value')
            if k is not None and v is not None:
                add_unit(k, v, 'shipLog')

    # Section 3: <table_ui>
    table_ui = root.find('table_ui')
    if table_ui is not None:
        for entry in table_ui.findall('TranslationTableEntryUI'):
            k, v = entry.find('key'), entry.find('value')
            if k is not None and v is not None:
                add_unit(k, v, 'ui')

    total = uid[0] - 1
    raw = ET.tostring(xliff, encoding='unicode')
    pretty = minidom.parseString(raw).toprettyxml(indent='  ', encoding='utf-8')
    with open(dst_path, 'wb') as f:
        f.write(pretty)

    print(f"完成：{total} 個 segment → {dst_path}")


# ── Mode 2: XLIFF → Translation.txt ──────────────────────────────────────────

def xliff_to_translation(xliff_path: str, original_path: str, dst_path: str):
    # Parse XLIFF — try with namespace, fall back without
    xtree = ET.parse(xliff_path)
    xroot = xtree.getroot()

    targets = {}  # id (str) → target text
    for tu in xroot.iter(f'{{{XLIFF_NS}}}trans-unit'):
        tid = tu.get('id')
        tgt = tu.find(f'{{{XLIFF_NS}}}target')
        if tid is not None and tgt is not None:
            targets[tid] = tgt.text or ''

    # Fallback: try without namespace (some tools strip it)
    if not targets:
        for tu in xroot.iter('trans-unit'):
            tid = tu.get('id')
            tgt = tu.find('target')
            if tid is not None and tgt is not None:
                targets[tid] = tgt.text or ''

    if not targets:
        print("錯誤：XLIFF 裡找不到任何 trans-unit，請確認格式正確。")
        sys.exit(1)

    # Parse original translation.txt and update <value> elements
    tree = ET.parse(original_path)
    root = tree.getroot()

    uid = 1
    updated = 0

    for entry in root.findall('entry'):
        v = entry.find('value')
        if v is not None:
            if str(uid) in targets:
                v.text = targets[str(uid)]
                updated += 1
            uid += 1

    shiplog = root.find('table_shipLog')
    if shiplog is not None:
        for entry in shiplog.findall('TranslationTableEntry'):
            v = entry.find('value')
            if v is not None:
                if str(uid) in targets:
                    v.text = targets[str(uid)]
                    updated += 1
                uid += 1

    table_ui = root.find('table_ui')
    if table_ui is not None:
        for entry in table_ui.findall('TranslationTableEntryUI'):
            v = entry.find('value')
            if v is not None:
                if str(uid) in targets:
                    v.text = targets[str(uid)]
                    updated += 1
                uid += 1

    tree.write(dst_path, encoding='utf-8', xml_declaration=True)
    print(f"完成：{updated} 個 segment 更新 → {dst_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def prompt_path(label: str) -> str:
    return input(f"{label}: ").strip().strip('"').strip("'")

def main():
    print("=== Outer Wilds CHT Translation Converter ===")
    print("1. Translation.txt → XLIFF（匯入 memoQ）")
    print("2. XLIFF → Translation.txt（翻譯完回組）")
    choice = input("選擇 (1/2): ").strip()

    if choice == '1':
        src = prompt_path("Translation.txt 路徑")
        dst = prompt_path("輸出 XLIFF 路徑（e.g. translation.xliff）")
        translation_to_xliff(src, dst)

    elif choice == '2':
        xliff   = prompt_path("XLIFF 路徑")
        original = prompt_path("原始 Translation.txt 路徑（用來保留結構）")
        dst     = prompt_path("輸出 Translation.txt 路徑")
        xliff_to_translation(xliff, original, dst)

    else:
        print("無效選擇，請輸入 1 或 2。")
        sys.exit(1)

if __name__ == '__main__':
    main()
