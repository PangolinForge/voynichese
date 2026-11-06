# Registration methodology and limitations

## Input and algorithm

The V3 run used the source Voynichese word rectangles, a local set of 213 unmodified high-resolution Yale TIFFs, and the installed `voynich_box_fit_v3/fit_all_pages.py` program. The rerun archive states these algorithmic enhancements: multi-peak candidate search, ±6° rotation fallback, 8% foldout margin, top/bottom padding, and shared-scale retry where panels share a TIFF.

The `fit_summary.csv` contains one row for each of 225 attempts. The 1 SKIP was `f101v2` (source text straddling two TIFFs). The 5 FAIL entries were `f70r2`, `f72r2`, `f72v2`, `f72v3`, and `f102v2`. The master CSV includes 224 attempted entries with actual rows.

## From V3 quadrilateral to XML

- Native `tiff_width` and `tiff_height` become `<folio width=... height=...>`.
- The original `word_index` is retained unchanged.
- For each four-corner word polygon, use `x=floor(min(all x))`, `y=floor(min(all y))`, `right=ceil(max(all x))`, `bottom=ceil(max(all y))`.
- Export `width=right-x`, `height=bottom-y`.
- Exclude flagged `zero_size`/`off_image` records and any invalid/outside-TIFF box from XML. **No clipping, no fabricated corrections.**
- Preserve all records, corner coordinates, statuses and flags in `registered_word_boxes_v3.csv`.

44 rows are excluded from XML; see the individual records and reasons in `data/excluded_from_xml.csv`. Those rows are not deleted from the authoritative CSV.

## Checks and cautions

- XML parses with ordinary XML parsers; `wordCount` matches each file's child count.
- Each exported rectangle lies wholly within its declared TIFF dimensions.
- `OK` is a heuristic quality category from V3. It does not show independent photo-to-photo registration accuracy.
- Direct XML-to-Yale comparison is not independent validation if the same transform is used to define both sides.
- A later independent-photo QC pilot produced strong results for f100r but provisional panel cases elsewhere; this early release does not elevate those provisional cases to verified matches.
- The original source transcription can have segmentation errors. EVA is an audit field, not a decipherment.

## Integrity

Check `export_manifest.json` for the source CSV SHA-256 and output counts. The uploaded archive's recorded SHA-256 value for the master CSV is `f5b3d740368f2facb165a66481960a47be361f64473e8c1e5eae9766bc562b4c`.
