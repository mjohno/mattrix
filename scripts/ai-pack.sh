#!/usr/bin/env bash

set -euo pipefail

# Usage:
#   ./ai-pack [source_dir1 source_dir2 ...] [--output archive.zip] [--max-size MB]
#
# Defaults:
#   source_dirs = current directory
#   output_zip = ./archive.zip
#   max_size_mb = 1
#
# Description:
#   A simple utility to create a zip archive of source files from one or more directories,
#   while respecting .gitignore rules when applicable, and excluding large or binary files.
#   Designed for packaging code for AI assistants, ensuring we only include relevant source files
#   without any unnecessary clutter.
#
#
# Design goals:
# - Preserve the existing workspace directory structure exactly
# - Do NOT rewrite, flatten, or restructure paths
# - Use `zip -@` to stream a curated file list
# - Avoid staging/copying files
#
# Key rule:
#   zip stores paths exactly as provided (relative to cwd)
#   => we must feed it correct relative paths

OUT_FILE="archive.zip"
MAX_SIZE_MB=1
SOURCE_DIRS=()

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      OUT_FILE="$2"
      shift 2
      ;;
    --max-size)
      MAX_SIZE_MB="$2"
      shift 2
      ;;
    *)
      SOURCE_DIRS+=("$1")
      shift
      ;;
  esac
done

# Default to current dir if none provided
if [[ ${#SOURCE_DIRS[@]} -eq 0 ]]; then
  SOURCE_DIRS=(".")
fi

MAX_SIZE_BYTES=$((MAX_SIZE_MB * 1024 * 1024))

WORKDIR="$(pwd)"

echo "Packaging directories: ${SOURCE_DIRS[*]}"
echo "Working directory (zip root): $WORKDIR"
echo "Output file: $OUT_FILE"
echo "Max file size: ${MAX_SIZE_MB}MB"
echo "Binary files: excluded"

# Common exclusions (fallback for non-git dirs)
# These must match both top-level and nested paths when scanning a parent
# workspace that contains multiple independent codebases.
EXCLUDES=(
  ".git"
  ".terraform"
  ".venv"
  "venv"
  "node_modules"
  "__pycache__"
  "dist"
  "build"
  ".idea"
  ".vscode"
)

# File-name exclusions used during fallback scanning.
FILE_EXCLUDES=(
  "*.pyc"
  "*.pyo"
  "*.log"
  "*.tmp"
  "*.swp"
  ".DS_Store"
)

TMP_LIST="$(mktemp)"
: > "$TMP_LIST"

# --- Collect files (absolute paths) ---
# Each source dir is handled independently.
# If it's a git repo, use its own .gitignore rules.
for SRC in "${SOURCE_DIRS[@]}"; do
  SRC_DIR="$(cd "$SRC" && pwd)"

  echo "Processing: $SRC_DIR"

  if git -C "$SRC_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "  Using git-aware selection (.gitignore respected)"

    git -C "$SRC_DIR" ls-files --cached --others --exclude-standard -z \
      | while IFS= read -r -d '' relpath; do
          printf '%s\n' "$SRC_DIR/$relpath"
        done >> "$TMP_LIST"
  else
    echo "  Using fallback file scan"

    find "$SRC_DIR" -type f | while IFS= read -r f; do
      rel="${f#"$SRC_DIR"/}"
      base="$(basename "$f")"

      skip=false

      # Exclude junk directories anywhere in the tree, not just at the root.
      # This covers parent workspaces that contain multiple nested repos.
      for dir in "${EXCLUDES[@]}"; do
        case "$rel" in
          "$dir"/*|*/"$dir"/*)
            skip=true
            break
            ;;
        esac
      done

      # Exclude common junk files by basename.
      if [[ "$skip" == false ]]; then
        for pattern in "${FILE_EXCLUDES[@]}"; do
          if [[ "$base" == $pattern ]]; then
            skip=true
            break
          fi
        done
      fi

      $skip || printf '%s
' "$f" >> "$TMP_LIST"
    done
  fi

done

# Deduplicate absolute paths
sort -u "$TMP_LIST" -o "$TMP_LIST"

# --- Filter by size + binary ---
FILTERED_LIST="$(mktemp)"

while IFS= read -r file; do
  [[ -f "$file" ]] || continue

  size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
  if (( size > MAX_SIZE_BYTES )); then
    echo "WARN: Skipping $file (size ${size} bytes)"
    continue
  fi

  # Binary detection (heuristic)
  if [[ $size -gt 0 ]]; then
    if file --mime "$file" | grep -q "charset=binary"; then
      echo "WARN: Skipping $file (binary file detected)"
      continue
    fi
  fi

  printf '%s\n' "$file" >> "$FILTERED_LIST"

done < "$TMP_LIST"

rm -f "$TMP_LIST"

# --- Convert to relative paths for zip ---
# Critical step:
# zip -@ expects paths relative to the current working directory.
# We DO NOT modify structure — only strip the absolute prefix.
ZIP_INPUT="$(mktemp)"

while IFS= read -r abs_file; do
  rel_path="${abs_file#"$WORKDIR"/}"

  # Ensure the file is actually under WORKDIR
  if [[ "$abs_file" == "$WORKDIR"/* ]]; then
    printf '%s\n' "$rel_path" >> "$ZIP_INPUT"
  else
    echo "WARN: Skipping $abs_file (outside working directory)"
  fi

done < "$FILTERED_LIST"

rm -f "$FILTERED_LIST"

# --- Create archive ---
# No staging required.
# zip will preserve directory structure exactly as provided.

if [[ ! -s "$ZIP_INPUT" ]]; then
  echo "No files to archive after filtering."
  rm -f "$ZIP_INPUT"
  exit 1
fi

rm -f "$OUT_FILE"
zip -q "$OUT_FILE" -@ < "$ZIP_INPUT"

rm -f "$ZIP_INPUT"

echo "Done. Archive created: $OUT_FILE"
