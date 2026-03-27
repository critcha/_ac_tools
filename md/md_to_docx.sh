#!/usr/bin/env bash
#
# md_to_docx.sh — Convert Markdown to DOCX using pandoc.
# Math equations ($...$, $$...$$) become native Word OMML equations.
#
# Usage:
#   ./md_to_docx.sh [--overwrite] <input.md> [output.docx]

set -euo pipefail

overwrite=false
if [[ "${1:-}" == "--overwrite" ]]; then
    overwrite=true
    shift
fi

command -v pandoc >/dev/null 2>&1 || { echo "ERROR: pandoc not installed. Install via: brew install pandoc" >&2; exit 1; }
[[ $# -ge 1 ]] || { echo "Usage: $0 [--overwrite] <input.md> [output.docx]" >&2; exit 1; }

input="$1"
[[ -f "$input" ]] || { echo "ERROR: File not found: $input" >&2; exit 1; }

output="${2:-${input}.docx}"

if [[ -f "$output" && "$overwrite" == false ]]; then
    echo "ERROR: Output file already exists: $output" >&2
    echo "  Use --overwrite to replace it." >&2
    exit 1
fi

# Use minimal reference doc (no font overrides) if it exists alongside this script
script_dir="$(cd "$(dirname "$0")" && pwd)"
ref_doc="$script_dir/md_to_docx_reference.docx"

echo "Converting: $input → $output"
if [[ -f "$ref_doc" ]]; then
    pandoc "$input" --reference-doc="$ref_doc" --columns=1 -o "$output"
else
    echo "  (warning: $ref_doc not found, using pandoc defaults)" >&2
    pandoc "$input" --columns=1 -o "$output"
fi
# Fix pandoc's hardcoded 7920-twip table width to match actual page dimensions
python3 "$script_dir/md_to_docx_postprocess.py" "$output"
echo "Done: $output"
