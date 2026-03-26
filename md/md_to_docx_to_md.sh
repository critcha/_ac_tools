#!/usr/bin/env bash
#
# md_to_docx_to_md.sh — Round-trip: Markdown → DOCX → Markdown.
# Produces both the intermediate .md.docx and the final .md.docx.md.
#
# Usage:
#   ./md_to_docx_to_md.sh [--overwrite] <input.md>

set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"

overwrite_flag=""
if [[ "${1:-}" == "--overwrite" ]]; then
    overwrite_flag="--overwrite"
    shift
fi

[[ $# -ge 1 ]] || { echo "Usage: $0 [--overwrite] <input.md>" >&2; exit 1; }

"$script_dir/md_to_docx.sh" $overwrite_flag "$1"
"$script_dir/docx_to_md.sh" $overwrite_flag "$1.docx"
