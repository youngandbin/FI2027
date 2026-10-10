#!/usr/bin/env bash
# Build main.pdf; logs to build/; prints errors, undefined refs/citations and open TODOs.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p build
run() { pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex > build/pdflatex.log 2>&1; }
run && (cd build && BIBINPUTS=.. bibtex main > bibtex.log 2>&1); run; run
cp build/main.pdf . 2>/dev/null
grep -E "^!" build/main.log | head
grep -E "undefined" build/main.log | sort -u | head
grep -E "Overfull" build/main.log | head -5
echo "TODO: $(grep -o '\\todo{' sections/*.tex main.tex | wc -l)  pending: $(grep -o '\\pending{' sections/*.tex | wc -l)"
pdfinfo main.pdf 2>/dev/null | grep Pages
