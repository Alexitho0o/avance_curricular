"""Una ejecución reproduce V25 desde V24 y las fuentes privadas fijadas por hash.

El ensamblado OOXML conserva gráficos, filtros, fórmulas y partes no soportadas
por una importación/exportación integral. Artifact Tool crea el complemento.
No es una reproducción cruda de R19: sus proxies pendientes no se reconstruyen.
"""
import argparse, copy, hashlib, json, os, subprocess, shutil
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZipInfo
from lxml import etree as E
from preparar import prepare,load,sha,write
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';N={'m':NS}
def t(n):return '{'+NS+'}'+n
def strings(z):
    return [''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
def inline(c,ss):
    if c.get('t')=='s':
        value=ss[int(c.findtext(t('v')))];c.remove(c.find(t('v')));c.set('t','inlineStr');E.SubElement(E.SubElement(c,t('is')),t('t')).text=value
def xml(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def assemble(src,fragment,dest):
    with ZipFile(src) as z,ZipFile(fragment) as f:
        assert z.testzip() is None and f.testzip() is None
        ss=strings(f);replacements={}
        for num,frag,allowed in [(56,1,set(range(33,47))),(57,2,set(range(12,18)))]:
            part=f'xl/worksheets/sheet{num}.xml';root=E.fromstring(z.read(part));fr=E.fromstring(f.read(f'xl/worksheets/sheet{frag}.xml'))
            sd=root.find(t('sheetData'));rows={int(r.get('r')):r for r in sd}
            for row in fr.find(t('sheetData')):
                rn=int(row.get('r'))
                if rn not in rows:rows[rn]=E.SubElement(sd,t('row'),r=str(rn))
                existing={c.get('r') for c in rows[rn]}
                for c in row:
                    letters=''.join(v for v in c.get('r') if v.isalpha());idx=0
                    for letter in letters:idx=idx*26+ord(letter)-64
                    if idx not in allowed:continue
                    assert c.get('r') not in existing,'No sobrescribir contenido: '+c.get('r')
                    new=copy.deepcopy(c);inline(new,ss);new.set('s','185' if rn in (1,5) else '184');rows[rn].append(new)
            # El fragmento puede materializar filas vacías que no existían: Excel
            # exige orden ascendente, incluso cuando no contienen valores.
            sd[:]=sorted(sd,key=lambda row:int(row.get('r')))
            for row in sd:
                if num==56:row.set('ht','60');row.set('customHeight','1')
                elif int(row.get('r'))<=18:row.set('ht',str(max(float(row.get('ht','15')),42)));row.set('customHeight','1')
            # Solo las nuevas columnas se ensanchan; se conserva la maqueta anterior.
            cols=root.find(t('cols'))
            if cols is None:cols=E.Element(t('cols'));root.insert(list(root).index(sd),cols)
            for i in sorted(allowed):E.SubElement(cols,t('col'),min=str(i),max=str(i),width=str(24 if num==57 else 30),customWidth='1')
            if num==56:root.find(t('dimension')).set('ref','A1:AT6379')
            else:
                root.find(t('dimension')).set('ref','A1:Q29')
                merges=root.find(t('mergeCells'))
                if merges is None:merges=E.Element(t('mergeCells'));root.insert(list(root).index(sd)+1,merges)
                for m in fr.findall('m:mergeCells/m:mergeCell',N):merges.append(copy.deepcopy(m))
                merges.set('count',str(len(merges)))
            replacements[part]=xml(root)
        # Extiende únicamente la tabla de vista, manteniendo su filtro y nombre.
        headers=load(Path(fragment).parent/'payload.json')['headers']
        for name in z.namelist():
            if name.startswith('xl/tables/') and name.endswith('.xml'):
                tab=E.fromstring(z.read(name))
                if tab.get('ref')=='A5:AF6379':
                    tab.set('ref','A5:AT6379')
                    af=tab.find(t('autoFilter'))
                    if af is None:af=E.Element(t('autoFilter'));tab.insert(0,af)
                    af.set('ref','A5:AT6379');tc=tab.find(t('tableColumns'))
                    for i,h in enumerate(headers,33):E.SubElement(tc,t('tableColumn'),id=str(i),name=h)
                    tc.set('count',str(len(tc)));replacements[name]=xml(tab)
        styles=E.fromstring(z.read('xl/styles.xml'))
        for xf in styles.find(t('cellXfs')):
            a=xf.find(t('alignment'))
            if a is None:a=E.SubElement(xf,t('alignment'))
            a.set('horizontal','center');a.set('vertical','center');xf.set('applyAlignment','1')
        for nf in styles.findall('m:numFmts/m:numFmt',N):
            if nf.get('formatCode')=='#,##0':nf.set('formatCode','[>=1000000]#"."000"."000;[>=1000]#"."000;0')
        replacements['xl/styles.xml']=xml(styles)
        dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
        assert not dest.exists(),'No sobrescribir una salida existente'
        with ZipFile(dest,'x',ZIP_DEFLATED) as d:
            for item in z.infolist():
                # Metadatos ZIP fijos para reproducibilidad byte a byte.
                info=ZipInfo(item.filename,(2026,10,30,0,0,0));info.compress_type=ZIP_DEFLATED
                d.writestr(info,replacements.get(item.filename,z.read(item.filename)))
        return list(replacements)
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--privado',required=True);p.add_argument('--salida',required=True);p.add_argument('--informes',required=True);p.add_argument('--node',required=True);p.add_argument('--node-modules',required=True);a=p.parse_args()
    private=Path(a.privado);out=Path(a.informes);prepare(a.config,private,out)
    # El enlace de dependencias solo existe en el área privada, nunca en Git.
    link=private/'node_modules'
    if not link.exists():link.symlink_to(a.node_modules,target_is_directory=True)
    shutil.copyfile(Path(__file__).with_name('construir.mjs'),private/'construir.mjs')
    subprocess.run([a.node,str(private/'construir.mjs'),str(private)],check=True)
    cfg=load(a.config);src=cfg['entradas']['v24']['ruta'];changed=assemble(src,private/'fragment.xlsx',a.salida)
    assert sha(src)==cfg['entradas']['v24']['sha256']
    with ZipFile(a.salida) as z:
        assert z.testzip() is None
        for n in z.namelist():
            if n.endswith('.xml'):E.fromstring(z.read(n))
        charts=len([n for n in z.namelist() if n.startswith('xl/charts/chart') and n.endswith('.xml')]);assert charts==13
    write(out/'ENSAMBLADO_V25.json',{'clase':'B/C','salida':str(Path(a.salida).resolve()),'sha256':sha(a.salida),'v24_sha256':sha(src),'componentes_modificados':changed,'graficos':charts,'base_ensamblado':'V24 intacta; complementos C1 en AG:AO y resumen L:Q de hoja57','tasas':'No se modifican fórmulas ni entradas de R19','limite':'Reproducción incremental V24 + fuentes de contexto; no reproduce R19 desde fuentes crudas. Recálculo nativo y filtros se verifican aparte.'})
if __name__=='__main__':main()
