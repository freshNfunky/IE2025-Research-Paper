#!/usr/bin/env bash
# Assemble a flat, self-contained arXiv source package (TeX + figures) and verify
# it compiles. arXiv wants the SOURCE, not the PDF. Output: build/arxiv.tar.gz
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$R/build/arxiv"
rm -rf "$OUT"; mkdir -p "$OUT"

# tex with a flat graphicspath (all assets sit next to the .tex on arXiv)
sed 's#\\graphicspath{{../figures/}{../images/}}#\\graphicspath{{./}}#' \
    "$R/paper/paper_v1.tex" > "$OUT/paper_v1.tex"

# only the referenced figures
cp "$R/images/YOLO-Traffic-Scene.png" "$OUT/"
for f in taxonomy_architecture benchmark_flat_vs_hier \
         ex_road_anomaly_01_0_abstracted ex_road_anomaly_08_1_abstracted \
         calibration_tradeoff; do
  cp "$R/figures/$f.png" "$OUT/"
done

# verify it compiles in a clean dir (proves arXiv will build it)
( cd "$OUT" && latexmk -pdf -interaction=nonstopmode -halt-on-error paper_v1.tex \
    >/dev/null 2>&1 ) && echo "compiles OK ($(cd "$OUT" && grep -c . paper_v1.tex) tex lines)"

# keep source only in the tarball
( cd "$OUT" && rm -f paper_v1.aux paper_v1.log paper_v1.out paper_v1.fls \
    paper_v1.fdb_latexmk paper_v1.synctex.gz )
tar czf "$R/build/arxiv.tar.gz" -C "$OUT" paper_v1.tex \
    YOLO-Traffic-Scene.png taxonomy_architecture.png benchmark_flat_vs_hier.png \
    ex_road_anomaly_01_0_abstracted.png ex_road_anomaly_08_1_abstracted.png \
    calibration_tradeoff.png
echo "arXiv package: $R/build/arxiv.tar.gz"
