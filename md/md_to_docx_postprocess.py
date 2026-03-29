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

# Register OOXML namespaces so ET.write() preserves the original prefixes
# instead of mangling them to ns0, ns1, etc.
_OOXML_NAMESPACES = {
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm':   'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'o':   'urn:schemas-microsoft-com:office:office',
    'v':   'urn:schemas-microsoft-com:vml',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'wp':  'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
}
for prefix, uri in _OOXML_NAMESPACES.items():
    ET.register_namespace(prefix, uri)

NS = _OOXML_NAMESPACES['w']
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


def _make_spacer_para(style_id, font_size_half_pt):
    """Create an empty paragraph with the given style and a small font size.

    Used as a vertical spacer inside shaded areas (blockquotes, code blocks).
    Pandoc collapses these on docx→md round-trip, so they vanish cleanly.
    """
    p = ET.Element(f'{W}p')
    pPr = ET.SubElement(p, f'{W}pPr')
    pStyle = ET.SubElement(pPr, f'{W}pStyle')
    pStyle.set(f'{W}val', style_id)
    spacing = ET.SubElement(pPr, f'{W}spacing')
    spacing.set(f'{W}before', '0')
    spacing.set(f'{W}after', '0')
    spacing.set(f'{W}line', str(font_size_half_pt * 10))
    spacing.set(f'{W}lineRule', 'exact')
    rPr = ET.SubElement(pPr, f'{W}rPr')
    sz = ET.SubElement(rPr, f'{W}sz')
    sz.set(f'{W}val', str(font_size_half_pt))
    return p


def add_shaded_block_padding(body, style_id):
    """Insert small spacer paragraphs before/after each block of the given style.

    Google Docs ignores style-level and direct paragraph spacing for padding
    inside shaded areas. The only reliable way to get visual padding is to
    insert empty paragraphs with the same style that carry the background
    color but take up minimal vertical space.
    """
    # Collect matching paragraphs (can't modify tree while iterating)
    matching = set()
    for p in body.iter(f'{W}p'):
        pPr = p.find(f'{W}pPr')
        if pPr is None:
            continue
        pStyle = pPr.find(f'{W}pStyle')
        if pStyle is not None and pStyle.get(f'{W}val') == style_id:
            matching.add(p)

    if not matching:
        return 0

    # Group consecutive matching paragraphs into blocks
    children = list(body)
    blocks = []
    current_block = []
    for child in children:
        if child in matching:
            current_block.append(child)
        else:
            if current_block:
                blocks.append(current_block)
                current_block = []
    if current_block:
        blocks.append(current_block)

    # Insert spacers around each block and add spacing after
    for block in blocks:
        first = block[0]
        last = block[-1]
        children = list(body)
        idx_first = children.index(first)
        idx_last = children.index(last)
        # Add spacing-before to the paragraph after the block
        if idx_last + 1 < len(children):
            next_p = children[idx_last + 1]
            next_pPr = next_p.find(f'{W}pPr')
            if next_pPr is not None:
                spacing = next_pPr.find(f'{W}spacing')
                if spacing is None:
                    spacing = ET.SubElement(next_pPr, f'{W}spacing')
                spacing.set(f'{W}before', '200')
        # Insert after last (do this first so indices stay valid)
        body.insert(idx_last + 1, _make_spacer_para(style_id, 8))
        # Insert before first
        body.insert(idx_first, _make_spacer_para(style_id, 10))

    return len(blocks)


def postprocess(docx_path):
    tmp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            z.extractall(tmp_dir)

        doc_path = os.path.join(tmp_dir, 'word', 'document.xml')
        tree = ET.parse(doc_path)
        root = tree.getroot()

        modified = False

        # Scale table widths
        text_width = get_text_width(root)
        if text_width != PANDOC_HARDCODED_WIDTH:
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
                modified = True
                print(f'  Scaled {scaled} table(s) from {PANDOC_HARDCODED_WIDTH} to {text_width} twips')

        # Add padding spacers around shaded blocks
        body = root.find(f'{W}body')
        if body is not None:
            for style_id, label in [('BlockText', 'blockquote'),
                                    ('SourceCode', 'code')]:
                padded = add_shaded_block_padding(body, style_id)
                if padded:
                    modified = True
                    print(f'  Added padding to {padded} {label} block(s)')

        if modified:
            tree.write(doc_path, xml_declaration=True, encoding='UTF-8')
            with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                for dirpath, _, filenames in os.walk(tmp_dir):
                    for fn in filenames:
                        full = os.path.join(dirpath, fn)
                        zout.write(full, os.path.relpath(full, tmp_dir))
    finally:
        shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <file.docx>', file=sys.stderr)
        sys.exit(1)
    postprocess(sys.argv[1])
