"""Cierra metadatos H006 después del QA técnico y la revisión visual/nativa.

No modifica libros, fuentes o análisis previos. Los datos nuevos son agregados.
"""
from pathlib import Path
from collections import Counter
import csv,json,re,subprocess
from construir import OUT,ROOT,BOOK,sha,dump,fuentes

def main():
    F=fuentes();q=json.loads((OUT/'QA_H006.json').read_text());r=json.loads((OUT/'RESULTADOS_H006.json').read_text());d=json.loads((OUT/'DATOS_H006.json').read_text())
    controls=[];public={}
    with open(F['PUBLICA']['ruta'],encoding='latin1') as f:
        for x in csv.DictReader(f,delimiter=';'):
            if x['CÓDIGO DE INSTITUCIÓN']=='162':public[x['CÓDIGO CARRERA'],int(x['AÑO'].removeprefix('MAT_'))]=x
    for i,y in enumerate(range(2019,2027)):
        for j,field in enumerate(['TOTAL MATRÍCULA','TOTAL MATRÍCULA PRIMER AÑO']):
            for row in d['tendencia']:
                source=[x for (c,a),x in public.items() if a==y and c.rsplit('V',1)[0]==row[0]]
                expected='E: sin dato' if any(x[field]=='' for x in source) else sum(int(x[field]) for x in source)
                actual=row[8+2*i+j]
                assert actual==expected,(row[0],y,field,actual,expected)
                controls.append(dict(control='Familia contra publicación',familia=row[0],anio=y,campo=field,esperado=expected,obtenido=actual))
    master=json.loads(Path(F['MAESTRO']['ruta']).read_text());expected=set()
    for x in master['oferta_anual']:
        key=(x['codigo_unico'],x['anio']);p=public.get(key)
        if x['vigencia']=='Vigente con estudiantes nuevos' and (p is None or p['TOTAL MATRÍCULA PRIMER AÑO']=='0'):expected.add(key)
    assert expected=={(x[1],int(x[0])) for x in d['no_abiertas']}
    controls.append(dict(control='Oferta con nuevos y sin primer año',esperado=len(expected),obtenido=len(d['no_abiertas'])))
    for x in d['antiguas']:
        assert x[10]==sum(x[11:15])
        assert x[6]<=2016 and x[19]>0
        controls.append(dict(control='Cohortes suman VIG1',familia=x[0],esperado=x[10],obtenido=sum(x[11:15])))
    dump(OUT/'CONTROL_INDEPENDIENTE_H006.json',controls)
    q.update(estado='PASS',control_independiente=len(controls),apertura_excel='B: ambos libros abiertos en Microsoft Excel sin aviso de reparación; cerrados sin guardar',revision_visual='B: nueve hojas del resumen y seis de retención revisadas en PNG; celdas centradas; gráficos y detalles legibles',observacion_recalculo='Las copias de prueba eliminan cachés de fórmulas antes de LibreOffice para forzar el cálculo con los selectores modificados.')
    q['retencion'].update(estado='PASS',apertura_excel='B: abierto sin reparación; cerrado sin guardar',revision_visual='B: seis hojas con centrado revisado')
    assert sha(OUT/BOOK)==q['sha256']
    desktop=Path.home()/'Desktop/ENTREGA_RETENCION_20261031'
    assert sha(desktop/BOOK)==q['sha256']
    ret=ROOT/'outputs/entrega_retencion_20261029';rb=ret/'ENTREGA_RETENCION_IPSS_20261029.xlsx'
    assert sha(rb)==q['retencion']['sha256']==sha(desktop/rb.name)
    dump(OUT/'DIFERENCIAS_H006.json',[])
    dump(OUT/'QA_H006.json',q)
    oldqa=json.loads((OUT/'QA.json').read_text());dump(OUT/'QA.json',dict(q,antecedente_H005c=oldqa.get('antecedente_H005c',oldqa)))
    dump(ret/'QA_FORMATO_H006.json',q['retencion'])
    year='; '.join(f'{a}: {n}' for a,n in r['no_abiertas_por_anio'].items())
    text=['# H006 · Resumen, carreras y formato de entrega','',
      'D · Alexi, 30-10-2026. Nuevas agregaciones autorizadas, sin reconstruir enlaces ni paridades. Sin commit/push en avance_curricular.',
      '',f"B/C: 4 familias con primera matrícula hasta 2016 y matrícula 2026; 78 VIG1. Tres sólo admiten antiguos en oferta 2027; una queda E. Rezago aproximado: 1; titulación proceso 2026: 38 registros en estas familias.",
      '«Quedan por titular» es el proxy D solicitado (VIG1), no una comprobación individual de ausencia de título. Titulación proceso 2026 corresponde a su ventana 2025–2026; no se descuenta de VIG1. Rezago C usa años enteros frente a duración de estudios/2.',
      '',f'B/C: 125 códigos-año ofertados con nuevos y sin fila pública de matrícula. No acredita una no apertura operativa. Por año: {year}. 2027 no evaluable hasta MU 2027.',
      '',f"C: tendencia en 77 familias/grupos: {r['tendencia']}. Prioridad explícita: CERRADA, NUEVA, EN_EXTINCION, ALZA/BAJA/ESTABLE. Primer año vacío en cualquier versión se muestra E, nunca cero. CERRADA sólo expresa total publicado 2026=0; no cierre administrativo. Dos códigos legados no descomponibles conservan sede/jornada/sector E; no se inventan equivalencias.",
      '', '## Mayores variaciones absolutas 2022–2026','', '| Familia | Carrera | 2022 | 2026 | Variación |','| --- | --- | ---: | ---: | ---: |']
    for x in r['top5_alzas']+r['top5_bajas']:text.append(f"| {x['familia']} | {x['carrera']} | {x['base2022']} | {x['matricula2026']} | {x['delta']:+} |")
    text+=['','Incluye familias NUEVAS y CERRADAS en los rankings: las barras comparan variación absoluta, no sólo las clases ALZA/BAJA.',
      '', '## QA y conservación','',f"39.546 controles de celdas del resumen, incluidos los 34.960 anteriores idénticos; {len(controls)} controles independientes de agregados. 745 fórmulas sin errores. Retención: 1.956 controles y 41 fórmulas sin errores. Doce escenarios de filtros, más Todas; reproducción de modelos idéntica.",
      'Se compararon todas las celdas pobladas preexistentes, sus fórmulas y sus valores recalculados: cero cambios. Sólo formato centrado/ajuste y nuevas hojas del resumen. Los 24 cambios ajenos y las fuentes se conservan. Ambos libros abren sin reparación en Excel; no se guardaron cambios desde Excel.',
      'El QA antiguo de H003 conserva su guardia histórica de HEAD; no se alteró. El QA H006 verifica el HEAD de esta tarea y repite sus 1.956 controles y 41 fórmulas.',
      '', '| Libro | SHA-256 (igual en Escritorio) |','| --- | --- |',f"| {BOOK} | {q['sha256']} |",f"| {rb.name} | {q['retencion']['sha256']} |",'',
      'Fuentes y hashes: FUENTES_FIJADAS.json + FUENTES_H006.json. Controles: CONTROL_CIFRAS.json, CONTROL_INDEPENDIENTE_H006.json y QA_H006.json. PNG: renders/ (paneles y detalles) y renders_h006/ (nueve hojas). Retención: renders_artifact/ y renders/.',
      '', '## Regla de centrado','', 'IPSS_IA_SKILLS_Y_REGLAS 1.3.10, commit c62b6908303ffcabdcfb44114ad0f0b0813da8a6, publicado. Codex idéntico a canónica. Vistas ejecutivas no impone una alineación de cuerpo contradictoria; no se modificó.',
      'Variante Claude: skills/claude/excel-formato-chile/SKILL.md; SHA-256 f9aeb966dbb6a7fc4a2ce91c7795dcfac318446172d2bd71393661bffabdc5a8. No instalada en claude.ai.']
    (OUT/'INFORME_H006.md').write_text('\n'.join(text)+'\n')
    (ret/'INFORME_FORMATO_H006.md').write_text('# Formato H006\n\nD · Alexi, 30-10-2026: todas las celdas con contenido centradas horizontal y verticalmente.\n\nB/C: 1.956 controles, 41 fórmulas, cero diferencias y cero errores. Se mantienen cifras, fuentes, fórmulas y tablas. Excel abre sin reparación. QA_FORMATO_H006.json registra el hash igual a la copia del Escritorio.\n')
    mp=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.json';m=json.loads(mp.read_text());rows=m['resultados']
    for x in rows:
        if x['id'] in ['R20','R21']:
            x.setdefault('sha256_antes_H006',x['sha256']);x['sha256']=q['sha256'] if x['id']=='R21' else q['retencion']['sha256'];x['actualizacion_H006']='Presentación centrada y QA repetido sin diferencias; nuevas hojas H006 sólo en resumen. Sin commit.'
            x['commit']='SIN_COMMIT H006 · base 430c7d4';x['alcance_commit']='La huella actual corresponde al derivado local H006, no al commit previo.'
            x['qa']='outputs/excel_resumen_cruce_20261030/QA_H006.json' if x['id']=='R21' else 'outputs/entrega_retencion_20261029/QA_FORMATO_H006.json'
    additions=[('R22','¿Qué familias antiguas conservan matrícula 2026?','4 familias; 78 VIG1; 3 sólo antiguos 2027 y 1 E; rezago aproximado 1; 38 registros de titulación proceso 2026.','6_Carreras_Antiguas'),('R23','¿Qué oferta con nuevos no registra primer año publicado?','125 códigos-año 2010–2026, todos sin fila pública. No prueba no apertura operativa. 2027 E hasta MU 2027.','7_Ofertadas_No_Abiertas'),('R24','¿Cómo varía la matrícula por familia entre 2022 y 2026?','77 familias/grupos: ALZA 10, BAJA 4, ESTABLE 2, NUEVA 40, EN_EXTINCION 0 y CERRADA 21; suma de versiones.','8_Tendencia_Matricula')]
    for id,question,result,sheet in additions:
        x=dict(id=id,pregunta=question,resultado_clave=result,archivo=str((OUT/BOOK).relative_to(ROOT)),hoja_o_seccion=sheet,sha256=q['sha256'],commit='SIN_COMMIT · base 430c7d4',alcance_commit='Derivado local H006',script_productor=str((OUT/'construir.py').relative_to(ROOT))+'; ampliar_h006.py; verificar_h006.py',clase='B/C datos y agregación; D alcance y rótulos; E límites',fecha_resultado='2026-10-30',anio_proceso_y_referencia='Matrícula 2007–2026; oferta 2010–2027; titulación proceso 2026',no_recalcular_salvo='Nueva fuente gobernada pertinente o corrección demostrada. No reconstruir enlaces ni paridades.',fuentes_adicionales=r['fuentes'],qa=str((OUT/'QA_H006.json').relative_to(ROOT)))
        rows[:]=[z for z in rows if z['id']!=id];rows.append(x)
    m['actualizacion_H006']='R20/R21: nueva huella de formato; R22–R24: agregaciones nuevas autorizadas, QA sin diferencias y filtros probados.';dump(mp,m)
    md=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.md';s=md.read_text();s=s.replace('## Mapa (21 resultados)','## Mapa (24 resultados)')
    for x in rows:
        if x['id'] not in ['R20','R21','R22','R23','R24']:continue
        line='| '+' | '.join(str(z).replace('|','/') for z in [x['id']+' · '+x['pregunta'],x['resultado_clave'],x['archivo']+' · '+x['hoja_o_seccion'],x['script_productor'],x['commit'],x['sha256'],x['clase'],x['fecha_resultado'],x['no_recalcular_salvo']])+' |'
        pat=r'^\| '+x['id']+r' · .*?$'
        if re.search(pat,s,re.M):s=re.sub(pat,lambda _:line,s,flags=re.M)
        else:
            pos=s.index('\n\n',s.index('| R21 ·'));s=s[:pos]+'\n'+line+s[pos:]
    s=s.replace('- **R20**: Estado QA reutilizado de H003c, no ejecutado otra vez en H004. Sin datos individuales.','- **R20**: H004 reutilizó QA H003c; H006 repite los controles tras centrar el formato. Sin datos individuales.')
    md.write_text(s)
    # Privacidad: patrones de identificación en todas las salidas de texto.
    # Los esquemas son de familia/código de carrera y conteos, nunca personas.
    patterns=[r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9kK]\b',r'(?<![A-Za-z0-9])\d{7,8}-[0-9kK](?![A-Za-z0-9])',r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}']
    checked=[];findings=[]
    for folder in [OUT,ret]:
        for f in sorted(folder.rglob('*')):
            if not f.is_file() or f.is_symlink() or any(a in f.parts for a in ['node_modules','__pycache__']):continue
            if f.suffix not in ['.json','.md','.csv','.py','.mjs','.ndjson','.txt','.log']:continue
            text=f.read_text(errors='strict');checked.append(str(f.relative_to(ROOT)))
            for i,line in enumerate(text.splitlines(),1):
                if any(re.search(p,line) for p in patterns):findings.append(dict(archivo=str(f.relative_to(ROOT)),linea=i))
    assert not findings,findings
    dump(OUT/'QA_PRIVACIDAD_H006.json',dict(estado='PASS',archivos_texto=len(checked),hallazgos=findings,archivos=checked,libros='Ambos revisados por verificar_h006.py; sólo tablas agregadas, sin campos individuales',alcance='RUT con DV y correos por patrón; esquema sin CODCLI/MRUN/nacimiento/contactos ni nombres de estudiantes'))
    initial=json.loads((Path.home()/'.local/share/ipss/h006_20261030/ESTADO_INICIAL.json').read_text())
    allowed=['outputs/excel_resumen_cruce_20261030/','outputs/entrega_retencion_20261029/','docs/MAPA_RESULTADOS_GOBERNADOS.']
    for p,h in initial['hashes'].items():
        if not any(p.startswith(a) for a in allowed):assert sha(ROOT/p)==h,p
    current=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).decode().splitlines()
    excluded=lambda ls:[s for s in ls if not any(a in s for a in allowed)]
    assert excluded(current)==excluded(initial['status'].splitlines())
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT).decode().strip()
    for folder in [OUT,ret]:
        p=folder/'MANIFEST.json';manifest=json.loads(p.read_text());manifest['actualizacion_H006']='D formato; B/C QA y agregados; sin commit';manifest['head_H006']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
        if folder==OUT:manifest['hito']='H005/H005b/H005c preservados; H006 agregado';manifest['fuentes_H006']=r['fuentes']
        manifest['salidas_H006']={str(f.relative_to(folder)):sha(f) for f in sorted(folder.rglob('*')) if f.is_file() and not f.is_symlink() and not any(a in f.parts for a in ['node_modules','__pycache__']) and f.name!='MANIFEST.json'}
        if isinstance(manifest.get('salidas'),dict):
            for name in manifest['salidas']:
                if (folder/name).is_file():manifest['salidas'][name]=sha(folder/name)
        dump(p,manifest)
    print(json.dumps({'estado':'PASS','controles_independientes':len(controls),'mapa_resultados':len(rows),'libro':q['sha256'],'retencion':q['retencion']['sha256']},ensure_ascii=False))

if __name__=='__main__':main()
