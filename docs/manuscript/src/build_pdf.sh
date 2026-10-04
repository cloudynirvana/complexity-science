#!/usr/bin/env bash
# Build a thesis: resolve citations, render HTML with MathML, print to PDF with headless Chromium.
# Needs: pip install pypandoc_binary pyyaml; a Chromium/Chrome binary (CHROME env var or on PATH).
# Usage: build_pdf.sh [src-stem] [output-name]   (defaults to Thesis #3)
set -euo pipefail
cd "$(dirname "$0")/.."
python src/build_thesis.py "${1:-thesis_03}" "${2:-thesis_03_identifiability_gate}"
NAME="${2:-thesis_03_identifiability_gate}" python - <<'PY'
import os, pypandoc
NAME = os.environ["NAME"]
pypandoc.convert_file(NAME + ".md", "html5", outputfile=NAME + ".html",
    extra_args=["--standalone", "--mathml", "--toc", "--toc-depth=2", "--embed-resources",
                "--css=src/print.css", "--resource-path=."])
PY
CHROME="${CHROME:-$(command -v chromium || command -v google-chrome || echo /opt/pw-browsers/chromium-1194/chrome-linux/chrome)}"
"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="${2:-thesis_03_identifiability_gate}.pdf" "${2:-thesis_03_identifiability_gate}.html" 2>/dev/null
rm -f "${2:-thesis_03_identifiability_gate}.html"
echo "wrote docs/manuscript/${2:-thesis_03_identifiability_gate}.pdf"
