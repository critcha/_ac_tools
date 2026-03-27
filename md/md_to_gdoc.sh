#!/usr/bin/env bash
#
# md_to_gdoc.sh — Convert Markdown to DOCX and copy to Google Drive.
#
# Usage:
#   ./md_to_gdoc.sh [--overwrite] <input.md> [output.docx]

set -euo pipefail

[[ -n "${AC_GOOGLE_DRIVE:-}" ]] || { echo "ERROR: \$AC_GOOGLE_DRIVE is not set" >&2; exit 1; }
[[ -d "$AC_GOOGLE_DRIVE" ]] || { echo "ERROR: \$AC_GOOGLE_DRIVE directory not found: $AC_GOOGLE_DRIVE" >&2; exit 1; }

script_dir="$(cd "$(dirname "$0")" && pwd)"

"$script_dir/md_to_docx.sh" "$@"

# Determine the output path (same logic as md_to_docx.sh)
args=("$@")
# Skip --overwrite if present
if [[ "${args[0]:-}" == "--overwrite" ]]; then
    input="${args[1]}"
    output="${args[2]:-${input}.docx}"
else
    input="${args[0]}"
    output="${args[1]:-${input}.docx}"
fi

filename="$(basename "$output")"
dest="${AC_GOOGLE_DRIVE%/}/$filename"
cp "$output" "$dest"
echo "Copied to: $dest"
