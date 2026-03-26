#!/usr/bin/env bash
#
# docx_to_md.sh — Convert DOCX to Markdown using pandoc.
# Native Word OMML equations become $...$ and $$...$$ math.
#
# Usage:
#   ./docx_to_md.sh [--overwrite] <input.docx> [output.md]

set -euo pipefail

overwrite=false
if [[ "${1:-}" == "--overwrite" ]]; then
    overwrite=true
    shift
fi

command -v pandoc >/dev/null 2>&1 || { echo "ERROR: pandoc not installed. Install via: brew install pandoc" >&2; exit 1; }
[[ $# -ge 1 ]] || { echo "Usage: $0 [--overwrite] <input.docx> [output.md]" >&2; exit 1; }

input="$1"
[[ -f "$input" ]] || { echo "ERROR: File not found: $input" >&2; exit 1; }

output="${2:-${input}.md}"

if [[ -f "$output" && "$overwrite" == false ]]; then
    echo "ERROR: Output file already exists: $output" >&2
    echo "  Use --overwrite to replace it." >&2
    exit 1
fi

echo "Converting: $input → $output"
pandoc "$input" -t markdown --wrap=preserve --extract-media=. -o "$output"
echo "Done: $output"
