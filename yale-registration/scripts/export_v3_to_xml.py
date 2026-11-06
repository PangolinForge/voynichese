#!/usr/bin/env python3
"""Lossless V3 CSV -> bounded, legacy-shaped Yale-native per-folio XML.

The original CSV is authoritative. XML coordinates are conservative integer
axis-aligned envelopes of V3 quadrilateral coordinates. Each exclusion is
listed in excluded_from_xml.csv rather than silently repaired or clipped.
No image files are ever read or changed.
"""
import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict, Counter
from pathlib import Path
from xml.etree import ElementTree as ET

REQUIRED = ('folio', 'tiff', 'status', 'score', 'word_index',
            'tiff_width', 'tiff_height', 'registered_x0', 'registered_y0',
            'registered_x1', 'registered_y1', 'flag', 'eva_audit_only')
QUAD = (('quad_tl_x', 'quad_tl_y'), ('quad_tr_x', 'quad_tr_y'),
        ('quad_br_x', 'quad_br_y'), ('quad_bl_x', 'quad_bl_y'))
FOLIO_RE = re.compile(r'f\d{1,3}[rv][1-6]?', re.I)
BAD_FLAGS = {'zero_size', 'off_image'}


def finite(row, key):
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError('nonfinite_' + key)
    return value


def coordinates(row, width, height):
    if any(pair[0] not in row or not row[pair[0]] or pair[1] not in row or not row[pair[1]] for pair in QUAD):
        # fallback is only for a CSV lacking quadrilateral columns
        points = [(finite(row, 'registered_x0'), finite(row, 'registered_y0')),
                  (finite(row, 'registered_x1'), finite(row, 'registered_y1'))]
    else:
        points = [(finite(row, x), finite(row, y)) for x,y in QUAD]
    x0 = math.floor(min(p[0] for p in points))
    y0 = math.floor(min(p[1] for p in points))
    x1 = math.ceil(max(p[0] for p in points))
    y1 = math.ceil(max(p[1] for p in points))
    if x1 <= x0 or y1 <= y0:
        raise ValueError('zero_or_negative_transformed_area')
    if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
        raise ValueError('transformed_box_outside_tiff')
    return (x0, y0, x1-x0, y1-y0)


def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def export(src, out):
    if not src.is_file():
        raise FileNotFoundError(src)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'registered_xml').mkdir(exist_ok=True)
    with src.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not set(REQUIRED).issubset(set(reader.fieldnames or [])):
            raise ValueError('Missing required columns: '+str(set(REQUIRED)-set(reader.fieldnames or [])))
        rows = list(reader)
    if not rows:
        raise ValueError('Source V3 CSV is empty')
    data = defaultdict(list)
    dimensions = {}
    status = Counter()
    included_by_status = Counter()
    reasons = Counter()
    failed = []
    flags = Counter()
    folio_status = defaultdict(Counter)
    seen = set()
    for row in rows:
        folio = row['folio'].strip()
        index = row['word_index'].strip()
        st = row['status'].strip() or 'UNKNOWN'
        fl = row['flag'].strip()
        status[st] += 1
        folio_status[folio][st] += 1
        if fl: flags[fl] += 1
        try:
            if not FOLIO_RE.fullmatch(folio):
                raise ValueError('invalid_folio_id')
            idx = int(index)
            if idx < 0:
                raise ValueError('negative_word_index')
            if (folio, idx) in seen:
                raise ValueError('duplicate_word_index')
            seen.add((folio, idx))
            width = int(finite(row, 'tiff_width'))
            height = int(finite(row, 'tiff_height'))
            if width <= 0 or height <= 0:
                raise ValueError('invalid_tiff_size')
            if folio in dimensions and dimensions[folio] != (width, height):
                raise ValueError('inconsistent_tiff_size')
            dimensions[folio] = (width, height)
            if fl in BAD_FLAGS:
                raise ValueError('flagged_' + fl)
            x,y,w,h = coordinates(row, width, height)
            data[folio].append((idx,x,y,w,h,row['eva_audit_only']))
            included_by_status[st] += 1
        except (ValueError, KeyError, OverflowError) as exc:
            reason = str(exc)
            reasons[reason] += 1
            failed.append({'folio': folio,'tiff':row['tiff'], 'word_index':index,
                           'status':st,'flag':fl,'reason':reason})

    for folio, words in sorted(data.items()):
        width, height = dimensions[folio]
        root = ET.Element('folio', {'name':folio, 'wordCount':str(len(words)),
                                    'width':str(width), 'height':str(height)})
        for index,x,y,w,h,eva in sorted(words, key=lambda item:item[0]):
            item = ET.SubElement(root,'word',{'index':str(index), 'x':str(x), 'y':str(y),
                                              'width':str(w), 'height':str(h)})
            item.text = eva
        ET.indent(root, space='  ')
        ET.ElementTree(root).write(out/'registered_xml'/f'{folio}.xml', encoding='utf-8',
                                   xml_declaration=True, short_empty_elements=False)

    write_csv(out/'excluded_from_xml.csv',failed,
              ['folio','tiff','word_index','status','flag','reason'])
    failed_keys = {(e['folio'], e['word_index']) for e in failed}
    write_csv(out/'registration_status_by_word.csv',[
        {'folio':row['folio'],'tiff':row['tiff'],'word_index':row['word_index'],
         'status':row['status'],'score':row['score'],'flag':row['flag'],
         'included_in_xml':'no' if (row['folio'],row['word_index']) in failed_keys else 'yes'}
        for row in rows],
        ['folio','tiff','word_index','status','score','flag','included_in_xml'])
    folio_summary=[]
    for folio in sorted(folio_status):
        counts=folio_status[folio]
        folio_summary.append({'folio':folio,'total':sum(counts.values()),
                              'ok':counts['OK'],'check':counts['CHECK'],
                              'fail':counts['FAIL'],
                              'xml_exported':len(data[folio]),
                              'xml_excluded':sum(1 for e in failed if e['folio']==folio)})
    write_csv(out/'folio_export_summary.csv',folio_summary,
              ['folio','total','ok','check','fail','xml_exported','xml_excluded'])
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    manifest={
        'schema':'v3_yale_spatial_export_v1',
        'input_csv':src.name,
        'input_sha256':sha,
        'input_rows':len(rows),
        'source_folios':len(folio_status),
        'xml_folios':len(data),
        'xml_words':sum(len(v) for v in data.values()),
        'xml_exclusions':len(failed),
        'input_status_by_word':dict(status),
        'xml_status_by_word':dict(included_by_status),
        'input_flags':dict(flags),
        'xml_exclusion_reasons':dict(reasons),
        'bounding_box_policy':'floor(min(corner)), ceil(max(corner)); no clipping; exclude flagged source boxes',
        'independent_verification':'NOT COMPLETE; folio status is heuristic',
        'geometry_source':'quad corners in registered_word_boxes_v3.csv'
    }
    (out/'export_manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(export(a.csv.expanduser().resolve(),a.out.expanduser().resolve()),indent=2))

if __name__=='__main__': main()
