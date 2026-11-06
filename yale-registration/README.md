# Yale TIFF coordinate registration — Stage 1

**Status:** Documentation published; the complete V3 data release is packaged but **NOT YET pushed** to this branch. Please do not cite the branch as the full dataset until the data import commit is present.

The genuine 6 November 2026 V3 rerun produced **37,673 registered word records** for **224 mapped folio/panel entries**, from **225 attempted**: 196 OK, 23 CHECK, 5 FAIL and 1 SKIP. These are *V3 heuristic fit statuses*, **not** independent photo-to-photo verification.

A separate ZIP release prepared from the uploaded V3 archive includes the authoritative CSV, fit reports, **224 Yale-native per-folio XML files** (37,629 exported word boxes), 44 logged XML exclusions, an exporter script and a one-command Mac Git publisher. The TIFF originals are not part of the publication.

The full release archive is supplied in the associated ChatGPT conversation as `VOYNICH_YALE_STAGE1_RELEASE_20261106.zip`. To complete public publication, download that archive, unzip it on your Mac, and run its `yale-registration/scripts/publish_stage1_on_mac.command` script. It publishes **only** to branch `yale-coordinate-registration` and leaves `master` and `wiki` unchanged.

The original V3 *fitting algorithm source* was not in the uploaded rerun archive. The generated coordinates can be exported to XML reproducibly, but the original image-fitting stage requires separately publishing that code.

See [METHODOLOGY.md](METHODOLOGY.md), [NOTICE.md](NOTICE.md), and [LICENSE](LICENSE) for limitations and attribution.
