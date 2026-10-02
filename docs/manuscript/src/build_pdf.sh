#!/usr/bin/env bash
# Build Thesis #3: resolve citations, render HTML with MathML, print to PDF with headless Chromium.
# Needs: pip install pypandoc_binary pyyaml; a Chromium/Chrome binary (CHROME env var or on PATH).
set -euo pipefail
cd "$(dirname "$0")/.."
python src/build_thesis_03.py
python - <<'PY'
import pypandoc
pypandoc.convert_file("thesis_03_identifiability_gate.md", "html5", outputfile="thesis_03_identifiability_gate.html",
    extra_args=["--standalone", "--mathml", "--toc", "--toc-depth=2", "--embed-resources",
                "--css=src/print.css", "--resource-path=."])
PY
CHROME="${CHROME:-$(command -v chromium || command -v google-chrome || echo /opt/pw-browsers/chromium-1194/chrome-linux/chrome)}"
"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=thesis_03_identifiability_gate.pdf thesis_03_identifiability_gate.html 2>/dev/null
rm -f thesis_03_identifiability_gate.html
echo "wrote docs/manuscript/thesis_03_identifiability_gate.pdf"
