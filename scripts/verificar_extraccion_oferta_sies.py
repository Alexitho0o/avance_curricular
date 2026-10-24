#!/usr/bin/env python3
"""Read-only verification of the 162 TSV against every row of the source XLSX.

Requires lxml. Outputs only institutional/program data, no student data.
The expected hashes are mandatory. Existing different outputs are never overwritten.
"""
import argparse
import csv
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path
from lxml import etree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def normalize_header(value):
    unaccented = ''.join(c for c in unicodedata.normalize('NFD', value)
                         if not unicodedata.combining(c))
    return re.sub(r'[^A-Z0-9]+', '_', unaccented.upper()).strip('_')


def write_json_no_clobber(path, report):
    """Write a deterministic new report, or accept an identical existing report."""
    payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    path.parent.mkdir(exist_ok=True, parents=True)
    if path.exists():
        if path.read_text(encoding='utf-8') != payload:
            raise FileExistsError('Existing different output will not be overwritten: ' + str(path))
    else:
        with path.open('x', encoding='utf-8') as f:
            f.write(payload)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--tsv', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-xlsx-sha256', required=True)
    parser.add_argument('--expected-tsv-sha256', required=True)
    parser.add_argument('--expected-source-records', type=int, default=396003)
    parser.add_argument('--expected-institution-records', type=int, default=747)
    args = parser.parse_args()
    if args.output.resolve() in {args.original.resolve(), args.tsv.resolve()}:
        raise ValueError('Output must not be a source file')
    before = {'original': sha(args.original), 'tsv': sha(args.tsv)}
    expected_hashes = {'original': args.expected_xlsx_sha256, 'tsv': args.expected_tsv_sha256}
    if before != expected_hashes:
        raise ValueError('Source SHA-256 mismatch; no output written')
    with args.tsv.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        tsv_fields = reader.fieldnames
        records = list(reader)
    if len(set(tsv_fields)) != len(tsv_fields) or any(None in r for r in records):
        raise ValueError('Malformed TSV header or row width')
    compared_fields = [c for c in tsv_fields if c not in {'fila_origen', 'hoja_origen'}]
    if len(compared_fields) != 69:
        raise ValueError('Expected exactly 69 original fields plus source locators')
    targets = {int(r['fila_origen']): r for r in records}
    if len(targets) != len(records):
        raise ValueError('Duplicate original row locator in TSV')
    if {r['hoja_origen'] for r in records} != {'in'}:
        raise ValueError('Unexpected source sheet locator')
    header = {}
    seen = set()
    source_institution_rows = set()
    differences = []
    row_count = 0
    exact_matches = 0
    with zipfile.ZipFile(args.original) as archive:
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        sheets = workbook.find(NS + 'sheets')
        sheet = next(s for s in sheets if s.get('name') == 'in')
        rel_id = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        target = next(r.get('Target') for r in relationships if r.get('Id') == rel_id)
        sheet_path = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        strings_root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        shared_strings = [''.join(si.itertext()) for si in strings_root]
        del strings_root

        def value(cell):
            kind = cell.get('t')
            v = cell.find(NS + 'v')
            if kind == 's':
                return shared_strings[int(v.text)] if v is not None else ''
            if kind == 'inlineStr':
                inline = cell.find(NS + 'is')
                return ''.join(inline.itertext()) if inline is not None else ''
            return v.text if v is not None and v.text is not None else ''

        def cells(row):
            return {re.sub(r'\d+', '', cell.get('r')): value(cell)
                    for cell in row if cell.tag == NS + 'c'}

        for _, row in ET.iterparse(archive.open(sheet_path), events=('end',), tag=NS + 'row'):
            row_number = int(row.get('r'))
            row_count += 1
            if row_number == 1:
                header = {column: normalize_header(v) for column, v in cells(row).items()}
                if len(set(header.values())) != len(header):
                    raise ValueError('Header normalization collision')
                institution_column = next(c for c, name in header.items() if name == 'CODIGO_IES')
            else:
                institution_cell = next((cell for cell in row
                    if cell.tag == NS + 'c' and cell.get('r') == institution_column + str(row_number)), None)
                institution_value = value(institution_cell) if institution_cell is not None else ''
                if institution_value == '162':
                    source_institution_rows.add(row_number)
                if row_number in targets:
                    actual = {header[column]: v for column, v in cells(row).items() if column in header}
                    expected = targets[row_number]
                    seen.add(row_number)
                    delta = [{'field': field, 'tsv': expected[field], 'xlsx': actual.get(field, '')}
                             for field in compared_fields
                             if expected[field] != actual.get(field, '')]
                    if delta:
                        differences.append({'source_row': row_number, 'differences': delta})
                    else:
                        exact_matches += 1
            row.clear()
            while row.getprevious() is not None:
                del row.getparent()[0]
    after = {'original': sha(args.original), 'tsv': sha(args.tsv)}
    report = {
        'original_path': str(args.original), 'derivative_path': str(args.tsv),
        'hashes_before': before, 'hashes_after': after,
        'expected_hashes': expected_hashes,
        'source_files_unchanged': before == after,
        'sheet': 'in', 'xml_rows_scanned_including_header': row_count,
        'institution_filter': 'CODIGO_IES exactly equals textual value 162',
        'original_ies162_rows': len(source_institution_rows),
        'tsv_rows': len(records), 'verified_rows': len(seen), 'identical_rows': exact_matches,
        'different_rows': len(differences), 'differences': differences,
        'missing_target_rows': sorted(set(targets) - seen),
        'ies162_rows_omitted_from_tsv': sorted(source_institution_rows - set(targets)),
        'tsv_rows_not_ies162': sorted(set(targets) - source_institution_rows),
        'compared_field_count': len(compared_fields), 'compared_fields': compared_fields,
        'original_header_mapping': header,
        'tsv_fields_without_original_header': sorted(set(compared_fields) - set(header.values())),
        'value_policy': 'Exact text comparison. XML sharedStrings/inlineStr are decoded; otherwise cached XML <v> text is used. Absent cells and absent values become empty string. No trimming, case/accent changes, numeric rounding, date conversion or category recoding.',
        'header_policy': 'Unicode NFD, drop combining marks, uppercase; each run outside A-Z/0-9 becomes underscore; trim boundary underscores. Reject collisions.',
    }
    checks = {
        'source_files_unchanged': before == after,
        'complete_sheet_scan_expected_size': row_count == args.expected_source_records + 1,
        'expected_institution_records': len(source_institution_rows) == args.expected_institution_records,
        'expected_tsv_records': len(records) == args.expected_institution_records,
        'all_original_fields_compared': len(header) == 69 and not report['tsv_fields_without_original_header'],
        'all_targets_present': not report['missing_target_rows'],
        'all_target_values_identical': exact_matches == len(records) and not differences,
        'institution_coverage_complete': not report['ies162_rows_omitted_from_tsv'],
        'institution_scope_exact': not report['tsv_rows_not_ies162'],
    }
    report['checks'] = checks
    report['status'] = 'PASS' if all(checks.values()) else 'FAIL'
    if report['status'] != 'PASS':
        raise ValueError('Verification failed: ' + ', '.join(k for k, passed in checks.items() if not passed))
    write_json_no_clobber(args.output, report)
    print(json.dumps({k: v for k, v in report.items() if k not in {
        'differences', 'original_header_mapping', 'compared_fields', 'value_policy', 'header_policy'}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
