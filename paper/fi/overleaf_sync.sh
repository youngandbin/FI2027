#!/usr/bin/env bash
# Overleaf round trip for a free Overleaf account (no git sync).
#   ./overleaf_sync.sh pack           -> build/overleaf_upload.zip (Overleaf: New Project > Upload Project)
#   ./overleaf_sync.sh unpack <zip>   -> extract an Overleaf "Download > Source" zip into build/overleaf_import/
#                                        and list files that differ from this folder (nothing is overwritten)
set -euo pipefail
cd "$(dirname "$0")"
FILES=(main.tex refs.bib sections figures tables)

case "${1:-}" in
  pack)
    mkdir -p build
    rm -f build/overleaf_upload.zip
    zip -qr build/overleaf_upload.zip "${FILES[@]}" -x '*.DS_Store'
    echo "Wrote $(pwd)/build/overleaf_upload.zip"
    ;;
  unpack)
    zip_path="$(realpath "${2:?usage: $0 unpack <overleaf.zip>}")"
    out=build/overleaf_import
    rm -rf "$out" && mkdir -p "$out"
    unzip -q "$zip_path" -d "$out"
    # Overleaf exports are sometimes wrapped in a second zip
    inner="$(find "$out" -maxdepth 1 -name '*.zip' | head -1)"
    if [ -n "$inner" ]; then unzip -q "$inner" -d "$out" && rm "$inner"; fi
    echo "Extracted to $(pwd)/$out. Differences:"
    for f in "${FILES[@]}"; do diff -rq "$f" "$out/$f" || true; done
    ;;
  *)
    echo "usage: $0 pack | unpack <overleaf.zip>" >&2
    exit 1
    ;;
esac
