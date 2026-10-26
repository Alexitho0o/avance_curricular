"""Add only internal OOXML hyperlinks, unsupported by the authoring runtime."""

import io
import sys
import zipfile
from pathlib import Path
from lxml import etree as ET


def main():
    path=Path(sys.argv[1])
    ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    relns='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    source=path.read_bytes()
    edits={}
    with zipfile.ZipFile(io.BytesIO(source)) as z:
        book=ET.fromstring(z.read('xl/workbook.xml'))
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets={r.get('Id'):r.get('Target') for r in rels}
        for sheet in book.findall(f'{{{ns}}}sheets/{{{ns}}}sheet'):
            name=sheet.get('name')
            if name not in ['Pendientes por campo','Diplomados para completar']:
                continue
            target=targets[sheet.get(f'{{{relns}}}id')]
            part=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            root=ET.fromstring(z.read(part))
            assert root.find(f'{{{ns}}}hyperlinks') is None
            links=ET.Element(f'{{{ns}}}hyperlinks')
            for i in range(48):
                c=chr(65+i) if i<26 else 'A'+chr(65+i-26)
                r=i+9
                if name=='Pendientes por campo':
                    refs=[f'B{r}',f'I{r}']
                    location=f"'Diplomados para completar'!{c}8"
                else:
                    refs=[f'{c}7',f'{c}8']
                    location=f"'Pendientes por campo'!B{r}"
                for ref in refs:
                    assert root.find(f"{{{ns}}}sheetData/{{{ns}}}row/{{{ns}}}c[@r='{ref}']") is not None
                    ET.SubElement(links,f'{{{ns}}}hyperlink',ref=ref,location=location,tooltip='Ir a la regla o al campo relacionado')
            after={'sheetPr','dimension','sheetViews','sheetFormatPr','cols','sheetData','sheetCalcPr','sheetProtection','protectedRanges','scenarios','autoFilter','sortState','dataConsolidate','customSheetViews','mergeCells','phoneticPr','conditionalFormatting','dataValidations'}
            position=next((i for i,e in enumerate(root) if ET.QName(e).localname not in after),len(root))
            root.insert(position,links)
            edits[part]=ET.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
        assert len(edits)==2
        result=io.BytesIO()
        with zipfile.ZipFile(result,'w') as out:
            for item in z.infolist():
                out.writestr(item,edits.get(item.filename,z.read(item.filename)))
    path.write_bytes(result.getvalue())


if __name__=='__main__':
    main()
