# Stage 1 methods and known limitations

The V3 run used source Voynichese word rectangles with original EVA audit transcriptions, a local set of **213 original Yale TIFF images**, and a locally installed `voynich_box_fit_v3/fit_all_pages.py` algorithm. The rerun report describes multi-peak candidate search, rotation fallback ±6°, 8% foldout search margin, top/bottom padding and shared-scale retries. No Yale image files are redistributed in this branch.

## 6 November 2026 V3 rerun

- 225 folio/panel attempts: 196 OK, 23 CHECK, 5 FAIL, 1 SKIP.
- 224 mapped folio/panel entries in the resulting word CSV.
- 37,673 registered word records, preserved in the authoritative CSV. SHA-256 `f5b3d740368f2facb165a66481960a47be361f64473e8c1e5eae9766bc562b4c`.
- 224 XML exports with 37,629 words. 44 boxes omitted from XML: 33 explicitly `zero_size`, 1 explicitly `off_image`, and 10 further positions outside the TIFF boundary.
- In the authoritative CSV every word retains its source and Yale coordinates, quadrilateral corners, source word index, EVA audit transcription, status and score.

For XML, each full four-corner registered polygon is outward-rounded to its axis-aligned integer bounding rectangle and compared to the TIFF pixel bounds. Excluded records remain intact in the CSV and are itemized in the release's exclusions sidecar.

## Verification boundary

V3 `OK` does **not** mean an independent photographic match has been confirmed. An independent low-resolution/Yale comparison was piloted; the multi-panel viewport selection remains provisional for many folios. Neither transcription segmentation nor glyph identity is independently certified here. Users must not claim pixel-perfect or independently verified Yale coordinates on the basis of these outputs alone.

The V3 input image-fitting program was not present in the latest uploaded results ZIP, so that pipeline stage cannot be reproduced using this publication alone. No decipherment claims are made.
