# Voynichese → Yale high-resolution coordinate registration

**Public research artifact — V3 algorithmic alignment, NOT fully independently verified.**

This dataset extends the original [Voynichese project](https://github.com/voynichese/voynichese) with word boxes transformed into the native pixel grids of high-resolution Yale Beinecke manuscript TIFFs. It contains **no Yale TIFFs**. Original source words and text are attributed to the Voynichese Project; see [NOTICE.md](NOTICE.md).

## What is included

| File | Purpose |
|---|---|
| `data/registered_word_boxes_v3.csv` | Authoritative full V3 data: 37,673 original+registered word records, including original coordinate values, Yale dimensions, quadrilateral corners, fit score and unverified EVA audit text. |
| `data/fit_summary.csv` | 225 attempted folio/panel fits, including 1 SKIP. |
| `data/batch_report_v3.json` | Original V3 run report with local file paths normalized for public release. |
| `data/registered_xml/f*.xml` | 224 legacy-shaped per-folio XML exports with native Yale TIFF dimensions and conservative integer pixel rectangles. |
| `data/export_manifest.json` | Machine-readable SHA-256 and full export accounting. |
| `data/excluded_from_xml.csv` | Every one of the 44 records excluded from the XML. |
| `data/registration_status_by_word.csv` | Per-word status and whether its box was exported. |
| `data/folio_export_summary.csv` | Per-folio record totals and exclusions. |
| `scripts/export_v3_to_xml.py` | Deterministic XML generator from the authoritative V3 CSV. |
| `scripts/publish_stage1_on_mac.command` | Optional GitHub branch publisher for the release ZIP, without touching source scans. |

## Reported V3 results

- **213** original Yale high-resolution source TIFFs used by the V3 run (not included)
- **225** folio/panel fit attempts: **196 OK, 23 CHECK, 5 FAIL, 1 SKIP**
- **224** folio/panels represented in the registered-word CSV
- **37,673** registered-word records, preserved in the master CSV
- **37,629** valid (within TIFF boundaries and not flagged) per-word XML exports
- **44** exclusions: 33 flagged `zero_size`; 1 flagged `off_image`; 10 additional registered boxes extending outside the native TIFF pixel frame

**Important:** V3 `OK` is a registration-algorithm status, **not independent photographic proof**. The later source-photograph QC pilot revealed uncertain foldout and multi-panel viewport geometry. Users should not treat these coordinates as transcription truth or independently verified bounding boxes. All `CHECK`/`FAIL` and geometrically questionable boxes require more review.

## Coordinate conventions

The master CSV retains original and Yale coordinate fields. The registered corner coordinates are `quad_tl_*`, `quad_tr_*`, `quad_br_*`, and `quad_bl_*`; use these for faithful geometry. The XML form represents each quadrilateral as its outward-rounded **axis-aligned bounding rectangle** and can be larger than the rotated quadrilateral. XML coordinate units are Yale TIFF **pixels**; its `width` and `height` attributes are the TIFF dimensions, **not** the original Voynichese viewport dimensions. Word indices remain original even when missing entries were excluded.

## Reproduce the XML export

From the release root:

```bash
python3 yale-registration/scripts/export_v3_to_xml.py \
  --csv yale-registration/data/registered_word_boxes_v3.csv \
  --out yale-registration/data
```

Inspect the printed counts and SHA-256; see `data/export_manifest.json` and `data/excluded_from_xml.csv`.

## Upstream / licence

The original Voynichese enhanced transcription and spatial XML dataset is identified as Apache License 2.0 by its upstream documentation. Copyright and provenance notices are in [NOTICE.md](NOTICE.md), with the Apache 2.0 text in [LICENSE](LICENSE). Yale's scanned photographs are **not** redistributed or relicensed. This release does not claim to decipher the Voynich manuscript.

## Reproducibility limitation

The original **V3 fitting algorithm source package** was not contained in the supplied rerun archive; only the generated data and fit report were. The exporter is included and reproducible, but V3 image-to-image registration itself cannot be fully reproduced from this release without the separately supplied V3 code and original source imagery. Do not claim full pipeline reproducibility from these files alone.
