#!/bin/bash

# 1. Check if the user forgot the filename
if [ -z "$1" ]; then
  echo "Oops! You forgot the filename."
  echo "Usage: ./md_to_sha256.sh filename"
  exit 1
fi

# 2. Use "$1" to reference the file passed by the user
cat "$1" | shasum -a 256

# shasum -a 256 "$1"