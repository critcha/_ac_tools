#!/usr/bin/env python3
"""Post-process a pandoc-generated DOCX to fix table column widths.

Pandoc hardcodes a 7920-twip (5.5") text width when calculating table gridCol
widths, regardless of the actual page dimensions. This causes tables to render
narrower than the page in renderers (like Google Docs) that use absolute gridCol
values rather than the tblW percentage.

This script reads the page dimensions from the DOCX sectPr, then scales all
gridCol widths so they sum to the actual text width. The tblW percentage is left
at 100% so the result is correct in both Google Docs and Microsoft Word.
"""

import sys
import zipfile
import xml.etree.ElementTree as ET
import os
import shutil
import tempfile

NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W = f'{{{NS}}}'
PANDOC_HARDCODED_WIDTH = 7920


def get_text_width(root):
    """Read page text width from sectPr, falling back to Letter/1" margins."""
    for sectPr in root.iter(f'{W}sectPr'):
        pgSz = sectPr.find(f'{W}pgSz')
        pgMar = sectPr.find(f'{W}pgMar')
        if pgSz is not None and pgMar is not None:
            page_w = int(pgSz.get(f'{W}w', '12240'))
            left = int(pgMar.get(f'{W}left', '1440'))
            right = int(pgMar.get(f'{W}right', '1440'))
            return page_w - left - right
    return 9360  # Letter with 1" margins


def scale_table_widths(docx_path):
    tmp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            z.extractall(tmp_dir)

        doc_path = os.path.join(tmp_dir, 'word', 'document.xml')
        tree = ET.parse(doc_path)
        root = tree.getroot()

        text_width = get_text_width(root)
        if text_width == PANDOC_HARDCODED_WIDTH:
            return  # No scaling needed

        scale = text_width / PANDOC_HARDCODED_WIDTH
        scaled = 0

        for tbl in root.iter(f'{W}tbl'):
            grid = tbl.find(f'{W}tblGrid')
            if grid is None:
                continue
            cols = grid.findall(f'{W}gridCol')
            if not cols:
                continue
            total = sum(int(c.get(f'{W}w', '0')) for c in cols)
            if abs(total - PANDOC_HARDCODED_WIDTH) > 100:
                continue  # Not a pandoc-generated table, skip
            for col in cols:
                old_w = int(col.get(f'{W}w', '0'))
                col.set(f'{W}w', str(round(old_w * scale)))
            scaled += 1

        if scaled:
            tree.write(doc_path, xml_declaration=True, encoding='UTF-8')
            with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                for dirpath, _, filenames in os.walk(tmp_dir):
                    for fn in filenames:
                        full = os.path.join(dirpath, fn)
                        zout.write(full, os.path.relpath(full, tmp_dir))
            print(f'  Scaled {scaled} table(s) from {PANDOC_HARDCODED_WIDTH} to {text_width} twips')
    finally:
        shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <file.docx>', file=sys.stderr)
        sys.exit(1)
    scale_table_widths(sys.argv[1])
