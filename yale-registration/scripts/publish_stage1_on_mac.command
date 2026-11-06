#!/bin/zsh
set -euo pipefail

# This launcher runs on the user's Mac. It publishes files from the extracted
# release ZIP, not from TIFF source files and not from the V3 working directory.
SOURCE="${0:A:h:h}"
ROOT="$HOME/Downloads/VOYNICH"
CHECKOUT="$ROOT/VOYNICHESE_STAGE1_GIT_CHECKOUT"
URL="https://github.com/PangolinForge/voynichese.git"
BRANCH="yale-coordinate-registration"
EXPECTED_SHA="f5b3d740368f2facb165a66481960a47be361f64473e8c1e5eae9766bc562b4c"

print '==============================================================='
print 'VOYNICH YALE V3 — STAGE 1 PUBLIC GITHUB BRANCH PUBLICATION'
print '==============================================================='
print "Source release: $SOURCE"

if [[ ! -f "$SOURCE/data/registered_word_boxes_v3.csv" ]]; then
  print -u2 'ERROR: Release ZIP is not completely extracted.'
  exit 1
fi
if [[ ! -f "$SOURCE/data/export_manifest.json" ]]; then
  print -u2 'ERROR: Missing export manifest.'
  exit 1
fi
python3 - "$SOURCE/data/registered_word_boxes_v3.csv" "$SOURCE/data/export_manifest.json" "$EXPECTED_SHA" <<'PY'
import csv,hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]); report=json.loads(Path(sys.argv[2]).read_text())
h=hashlib.sha256(p.read_bytes()).hexdigest()
with p.open(newline='',encoding='utf-8-sig') as f:
    count=sum(1 for _ in csv.DictReader(f))
assert count==37673, ('Unexpected row count',count)
assert h==sys.argv[3] and h==report['input_sha256'],('Unexpected CSV hash',h)
assert report['xml_words']==37629 and report['xml_exclusions']==44,report
print('Verified registered words:',count,'SHA-256:',h)
PY

if [[ -e "$CHECKOUT" && ! -d "$CHECKOUT/.git" ]]; then
  print -u2 "ERROR: $CHECKOUT exists but is not a Git checkout."
  exit 1
fi
if [[ ! -d "$CHECKOUT/.git" ]]; then
  mkdir -p "$ROOT"
  git clone --single-branch --branch "$BRANCH" "$URL" "$CHECKOUT"
else
  [[ -z "$(git -C "$CHECKOUT" status --porcelain)" ]] || {
    print -u2 'ERROR: Existing checkout contains changes. Nothing pushed.'
    exit 1
  }
  git -C "$CHECKOUT" switch "$BRANCH"
  git -C "$CHECKOUT" pull --ff-only origin "$BRANCH"
fi

# Copy the complete tested release, replacing only our dedicated folder.
DEST="$CHECKOUT/yale-registration"
mkdir -p "$DEST"
rsync -a --delete --exclude 'publish_stage1_on_mac.command' "$SOURCE/" "$DEST/"
cp "$SOURCE/scripts/publish_stage1_on_mac.command" "$DEST/scripts/"

# Commit only our dedicated folder. The master/wiki branches and TIFFs are safe.
git -C "$CHECKOUT" add -- yale-registration
if git -C "$CHECKOUT" diff --cached --quiet; then
  print 'Branch already contains this exact release. No changes to push.'
  exit 0
fi

git -C "$CHECKOUT" diff --cached --stat
print ''
print 'Publishing to the PUBLIC branch:'
print "  $URL"
print "  $BRANCH"
print 'This does NOT push to master, and NO Yale TIFFs are included.'

git -C "$CHECKOUT" commit -m 'Publish V3 Yale-coordinate dataset and 224 per-folio XML exports'
git -C "$CHECKOUT" push origin "$BRANCH"
print ''
print "SUCCESS: https://github.com/PangolinForge/voynichese/tree/$BRANCH"
