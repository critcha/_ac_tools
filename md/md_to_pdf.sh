#!/bin/bash

# 1. Check if the user forgot the filename
if [ -z "$1" ]; then
  echo "Oops! You forgot the filename."
  echo "Usage: md_to_pdf filename"
  exit 1
fi

BASENAME="${1%.md}"
MD_FILE="${BASENAME}.md"
PDF_FILE="${BASENAME}.pdf"

# 2. Safety check: Does the markdown file actually exist?
if [ ! -f "$MD_FILE" ]; then
  echo "Error: I can't find a file named '$MD_FILE' in this folder."
  exit 1
fi

# 3. SMART STYLING: Check if md_to_pdf.typ exists in this folder
STYLE_FLAG=""
if [ -f "md_to_pdf.typ" ]; then
  echo "🎨 Found md_to_pdf.typ! Applying custom styles..."
  STYLE_FLAG="--include-in-header=md_to_pdf.typ"
fi

# 4. The initial run & opening Skim
echo "Converting $MD_FILE to PDF..."
pandoc "$MD_FILE" -o "$PDF_FILE" --pdf-engine=typst $STYLE_FLAG

echo "Opening Skim in the background..."
open -g -a Skim "$PDF_FILE"

# 5. The Watcher
echo "👀 Watching for changes... (Press Ctrl+C to stop)"

# How this works: 'ls -1' lists the files (one per line). 
# '2>/dev/null' silently hides the error if md_to_pdf.typ doesn't exist.
# Then we pipe that list directly into entr.
ls -1 "$MD_FILE" md_to_pdf.typ 2>/dev/null | entr -p pandoc "$MD_FILE" -o "$PDF_FILE" --pdf-engine=typst $STYLE_FLAG