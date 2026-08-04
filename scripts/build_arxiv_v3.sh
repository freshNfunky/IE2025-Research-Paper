#!/usr/bin/env bash
# Assemble a flat, self-contained arXiv source package for paper v3 (TeX + bib +
# figures) and verify it compiles. arXiv wants the SOURCE, not the PDF. We ship
# the pre-built .bbl so arXiv does not need our two-file bibliography.
# Output: build/arxiv_v3.tar.gz
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$R/build/arxiv_v3"
rm -rf "$OUT"; mkdir -p "$OUT"

# tex with a flat graphicspath (all assets sit next to the .tex on arXiv)
sed 's#\\graphicspath{{../figures/}{../images/}}#\\graphicspath{{./}}#' \
    "$R/paper/paper_v3.tex" > "$OUT/paper_v3.tex"

# bibliography: both source .bib files, plus a freshly built .bbl (robust on arXiv)
cp "$R/paper/bib.bib" "$R/paper/bib_v3.bib" "$OUT/"

# only the referenced figures
for f in title_scene_annotated taxonomy_architecture howc_01 depth3d_04 \
         v3_openworld_benchmark; do
  cp "$R/figures/$f.png" "$OUT/"
done

# build once in the clean dir to generate the .bbl and prove it compiles
( cd "$OUT" && latexmk -pdf -interaction=nonstopmode -halt-on-error paper_v3.tex \
    >/dev/null 2>&1 ) && echo "compiles OK ($(grep -c . "$OUT/paper_v3.tex") tex lines, \
$(cd "$OUT" && pdfinfo paper_v3.pdf 2>/dev/null | awk '/Pages/{print $2}') pages)"

# keep source + the generated .bbl (and the rendered PDF for local review); drop
# the rest of the build artifacts. The PDF stays in the folder but is deliberately
# NOT added to the tar below: arXiv builds its own PDF from the source.
( cd "$OUT" && rm -f paper_v3.aux paper_v3.log paper_v3.out paper_v3.fls \
    paper_v3.fdb_latexmk paper_v3.synctex.gz paper_v3.blg )

tar czf "$R/build/arxiv_v3.tar.gz" -C "$OUT" \
    paper_v3.tex paper_v3.bbl bib.bib bib_v3.bib \
    title_scene_annotated.png taxonomy_architecture.png howc_01.png \
    depth3d_04.png v3_openworld_benchmark.png
echo "arXiv v3 package: $R/build/arxiv_v3.tar.gz"
tar tzf "$R/build/arxiv_v3.tar.gz"
