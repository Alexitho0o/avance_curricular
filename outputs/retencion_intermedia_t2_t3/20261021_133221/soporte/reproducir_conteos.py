"""Read-only source analysis; outputs aggregates only, never student identifiers."""
from pathlib import Path
from collections import Counter, defaultdict
import contextlib, io, json, hashlib, datetime, subprocess
import openpyxl

ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular')
PREFIX=ROOT/'outputs/retencion_intermedia_t2_t3'
TARGET=Path('/tmp/retencion_counts.json')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources=[]
def add_source(path,sheet,expected=None):
    path=Path(path); h=sha(path)
    if expected: assert h==expected,(path.name,'unexpected hash')
    if not any(s['path']==str(path) and s['sheet']==sheet for s in sources):
        sources.append({'path':str(path),'sheet':sheet,'sha256_before':h})
    return path
rawpath=add_source(ROOT/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx','BASE_RETENCION_MU','19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd')
enginepath=add_source(ROOT/'outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx','02_COHORTE_ELEGIBILIDAD / 01_CATALOGO_CARRERA','5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3')
script=add_source(PREFIX/'20261020_215248/profile.py','read-only prefix before specs=','39b64cfea7773f269a10ba9576f1945f79e35e0f69a681913a173a2b279c0d88')
old={ '__file__':str(script)}
with contextlib.redirect_stdout(io.StringIO()): exec(compile(script.read_text().split('specs=',1)[0],str(script),'exec'),old)
base,raw,key,records,txt=old['base'],old['raw'],old['key'],old['records'],old['txt']
inc={y:[b for b in base if b['engine']['ANIO_INFORMADO']==y and b['engine']['ESTADO_FINAL']=='INCLUIDO']for y in (2024,2025)}
assert [len(inc[y]) for y in (2024,2025)]==[558,1150]
assert [len({(b['raw']['TIPO_DOC'],b['raw']['N_DOC'],b['raw']['DV'])for b in inc[y]})for y in (2024,2025)]==[558,1150]
specs=[('2025-T2','*T2_2025*','T2_2025',2024,'ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3'),('2025-T3','*T3_2025*','T3_2025',2024,'68a1cd54ee48c1e6a679c1dbb3999e12d491543e9425e81f3d0508fefdc8d6cc'),('2026-T2','*13_07*','Hoja1',2025,'7926a9cabcc67ed19abb50459132fd74ebb323bff9f5cb53e9116378c21a6769'),('2026-T3','*02_10*','Base',2025,'de4e73ee7d27779cdc531c6816f745d412e1021cbd61e4fceb8ab0459cbda4ae')]
closures=[]; by_career=[]
for close,pat,sheet,cohort,expected in specs:
    paths=list(Path('/Users/alexi/Downloads/cierre').glob(pat)); assert len(paths)==1
    path=add_source(paths[0],sheet,expected); w=openpyxl.load_workbook(path,read_only=True,data_only=True); rr=records(w[sheet]);w.close()
    idx=defaultdict(list)
    for r in rr:
        k=key(r.get('RUT'))
        if k:idx[k].append(r)
    has_state=bool(rr) and 'ESTADOACADEMICO' in rr[0]
    def summary(bb):
        found=[b for b in bb if b['key'] and idx.get(b['key'])]
        return {'denominator':len(bb),'comparable_document_keys':sum(bool(b['key'])for b in bb),'without_comparable_document_key':sum(not b['key']for b in bb),'persons_found':len(found),'persons_with_observed_VIGENTE':sum(any(r.get('ESTADOACADEMICO')=='VIGENTE' for r in idx[b['key']])for b in found) if has_state else None,'state_field':has_state,'persons_not_found_with_key':sum(bool(b['key'])and not idx.get(b['key'])for b in bb),'matched_rows_all_enrolments':sum(len(idx[b['key']])for b in found),'matched_people_multiple_rows':sum(len(idx[b['key']])>1 for b in found)}
    closures.append({'cohort':cohort,'closure':close,'source':str(path),'sheet':sheet,'source_rows':len(rr),**summary(inc[cohort]),'rate':'Pendiente','accredited_VIGENTE_at_closure':'Pendiente','class':'B/C observed presence; E coverage/date/state not accredited'})
    for career in sorted({b['engine']['NOMBRE_CARRERA']for b in inc[cohort]}):
        bb=[b for b in inc[cohort]if b['engine']['NOMBRE_CARRERA']==career]
        by_career.append({'cohort':cohort,'closure':close,'career':career,**summary(bb)})
assert [c['persons_found']for c in closures]==[1,325,2,0]
assert [c['persons_with_observed_VIGENTE']for c in closures]==[1,317,None,0]
annualscript=add_source(PREFIX/'20261020_221157/profile.py','read-only prefix before profile.json write','cd8d1d5445dcab9637645959f49628826552b108010ce6b45fab177d8bc225eb')
manifest=add_source(rawpath.parent/'MANIFEST_BASE_RETENCION_MU_2022_2026.json','manifest','746539ed62a3a3a051da14fd7f32b90fc6fd30a426304386d54e19c203d74145')
ann={'__file__':str(annualscript)}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(annualscript.read_text().split("(T/'profile.json').write_text",1)[0],str(annualscript),'exec'),ann)
annual=ann['totals']
assert [annual[k]['students']for k in ['2025-T2','2025-T3']]==[222,124]
assert [annual[k]['continue']for k in ['2025-T2','2025-T3']]==[74,48]
for k,v in annual.items():v['rate']=v['continue']/v['students'];v['class']='C/D annual follow-up; not intermediate retention'
candidates=[]
for sid,path,h in [
 ('10246','/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx','b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869'),
 ('11998','/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx','5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35')]:
    path=add_source(path,'Hoja1',h);w=openpyxl.load_workbook(path,read_only=True,data_only=True);rr=records(w['Hoja1']);w.close();idx=defaultdict(list)
    for r in rr:
        k=key(r.get('RUT'))
        if k:idx[k].append(r)
    for cohort in (2024,2025):
        bb=inc[cohort]; found=[b for b in bb if b['key']and idx.get(b['key'])]
        mrows=[r for b in found for r in idx[b['key']]]
        candidates.append({'source':sid,'source_path':str(path),'sheet':'Hoja1','cohort':cohort,'denominator':len(bb),'source_rows':len(rr),'comparable_document_keys':sum(bool(b['key'])for b in bb),'without_document_key':sum(not b['key']for b in bb),'persons_found_by_exact_RUT':len(found),'matched_rows_all_enrolments':len(mrows),'persons_multiple_rows':sum(len(idx[b['key']])>1 for b in found),'persons_any_observed_VIGENTE':sum(any(txt(r.get('ESTADOACADEMICO'))=='VIGENTE' for r in idx[b['key']])for b in found),'observed_states_rows':dict(Counter(txt(r.get('ESTADOACADEMICO'))for r in mrows)),'observed_enrolment_years_rows':dict(Counter(txt(r.get('ANOMATRICULA'))for r in mrows)),'class':'B/C snapshot-only presence by document; E date/coverage/state at closure; excludes 20 P pending explicit bridge','used_for_closure_numerator':False})
for s in sources:
    s['sha256_after']=sha(s['path']);assert s['sha256_before']==s['sha256_after']
result={'created':datetime.datetime.now().astimezone().isoformat(),'method':'Exact historical eligibility logic in memory; exact normalized document+DV lookup for TIPO_DOC R; count persons once, preserve all matched enrolment rows. Annual follow-up separately uses all source entry-period persons regardless of state. No fuzzy matches, no source edits, no individual outputs.','denominators':[558,1150,222,124],'closures':closures,'closure_by_career':by_career,'annual_separate':annual,'annual_controls':ann['extra'],'candidate_snapshots_by_document':candidates,'sources':sources,'qa':{'original_hashes_unchanged':True,'historical_counts_reproduced':True,'denominator_person_unique':True,'individual_identifiers_written':False,'rates_intermediate_calculated':False},'git':{'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'mutation_performed':False}}
TARGET.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# Reproducción de conteos de retención intermedia','', 'B/C: conteos históricos reproducidos desde las fuentes originales sin modificar motores, fuentes ni denominadores. E: no se acredita cobertura ni fecha efectiva del cierre con estos conteos.','', '| Cohorte | Cierre | Denominador | Presencias en listado | VIGENTE observado | Sin llave documental histórica |','|---|---|---:|---:|---:|---:|']
for c in closures:lines.append(f"| {c['cohort']} | {c['closure']} | {c['denominator']} | {c['persons_found']} | {c['persons_with_observed_VIGENTE'] if c['state_field'] else 'Sin campo'} | {c['without_comparable_document_key']} |")
lines+=['','Las 20 personas P no se computan como ausencia. Su ampliación de llaves es una revisión independiente por correspondencia explícita. Ninguna observación de respaldo se suma automáticamente a estos listados.','','## Ejercicio anual separado']
for k,v in annual.items():lines.append(f"- {k}: {v['continue']}/{v['students']} = {v['rate']:.8%}; localizados {v['found']}, solo VIG0 {v['onlyzero']}, ausentes {v['absent']}.")
lines+=['','## Presencia en respaldos por documento, sin inferencia temporal','', '| Fuente | Cohorte | Denominador | Buscables por RUT | Encontrados | Alguna VIGENTE observada | Matrículas encontradas |','|---|---|---:|---:|---:|---:|---:|']
for c in candidates:lines.append(f"| {c['source']} | {c['cohort']} | {c['denominator']} | {c['comparable_document_keys']} | {c['persons_found_by_exact_RUT']} | {c['persons_any_observed_VIGENTE']} | {c['matched_rows_all_enrolments']} |")
lines+=['','Estos respaldos pueden contener matrículas de distintos años y varias matrículas por persona. No son numeradores T2/T3. Las 20 P de cohorte 2025 quedan fuera de esta búsqueda documental y deben integrarse solo con el puente explícito verificado por la revisión de llaves.','','## QA','- Denominadores 558, 1.150, 222 y 124 reproducidos.','- Presencias 1, 325, 2 y 0 reproducidas.','- VIGENTE observados 1, 317, sin campo y 0 reproducidos.','- Todos los hashes de fuentes coinciden antes y después.','- Cero identificadores individuales escritos.','- Sin commit, push, cambio de rama o modificación del motor anual.']
Path('/tmp/retencion_counts.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'closures':closures,'annual_separate':annual,'candidates':candidates,'sources_verified':len(sources)},ensure_ascii=False,indent=2))
