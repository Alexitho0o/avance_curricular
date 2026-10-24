"""Clear inherited guide visibility only; cell values, formulas and all other ZIP parts are preserved."""
import json
from pathlib import Path
import posixpath
import sys
import zipfile

from lxml import etree

MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
DOC_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG_REL = 'http://schemas.openxmlformats.org/package/2006/relationships'


def normalize(path):
    path = Path(path)
    with zipfile.ZipFile(path) as archive:
        workbook = etree.fromstring(archive.read('xl/workbook.xml'))
        sheets = workbook.findall(f'{{{MAIN}}}sheets/{{{MAIN}}}sheet')
        guide = next(s for s in sheets if s.get('name') == 'Guía para editar')
        relation = guide.get(f'{{{DOC_REL}}}id')
        relationships = etree.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        target = next(r.get('Target') for r in relationships.findall(f'{{{PKG_REL}}}Relationship') if r.get('Id') == relation)
        sheet_path = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl', target))
        root = etree.fromstring(archive.read(sheet_path))
        cells_before = [etree.tostring(c) for c in root.findall(f'.//{{{MAIN}}}c')]
        hidden = 0
        for row in root.findall(f'{{{MAIN}}}sheetData/{{{MAIN}}}row'):
            if row.get('hidden') in ['1','true']:
                hidden += 1
            row.attrib.pop('hidden', None)
        filters = root.findall(f'{{{MAIN}}}autoFilter')
        for element in filters:
            root.remove(element)
        assert cells_before == [etree.tostring(c) for c in root.findall(f'.//{{{MAIN}}}c')]
        revised = etree.tostring(root, encoding='UTF-8', xml_declaration=True)
        temporary = path.with_suffix(path.suffix + '.visibility.tmp')
        with zipfile.ZipFile(temporary,'w') as out:
            for member in archive.infolist():
                out.writestr(member, revised if member.filename == sheet_path else archive.read(member.filename))
    temporary.replace(path)
    return {'guide_hidden_rows_cleared':hidden,'guide_filters_cleared':len(filters),
            'cell_values_and_formulas_preserved':True,'other_worksheets_preserved':True}


if __name__ == '__main__':
    print(json.dumps(normalize(sys.argv[1])))
