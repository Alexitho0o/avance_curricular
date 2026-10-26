"""Independent read-only QA. No individual values are emitted or written publicly."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,re,os
from collections import Counter
import openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
O=R/'outputs/retencion_intermedia_t2_t3/20261021_144031'
P=R/'.local_restricted/retencion_intermedia/20261021_144031'
OLD=R/'outputs/retencion_intermedia_t2_t3/20261021_133221'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=json.loads((P/'payload.json').read_text())
f=P/'DETALLE_PRIVADO_RETENCION_INTERMEDIA_20261021_144031.xlsx'
checks=[]
def check(n,v):
 checks.append({'control':n,'OK':bool(v)})
 if not v:raise AssertionError(n)
check('private_directory_mode_0700',(P.stat().st_mode&0o777)==0o700)
check('private_workbook_mode_0600',(f.stat().st_mode&0o777)==0o600)
check('private_xlsx_and_json_git_ignored',all(subprocess.run(['git','check-ignore','-q',str(P/n)],cwd=R).returncode==0 for n in ['payload.json',f.name]))
check('private_files_not_tracked',not subprocess.check_output(['git','ls-files',str(P)],cwd=R,text=True).strip())
check('xlsx_zip_crc_intact',zipfile.ZipFile(f).testzip() is None)
v=openpyxl.load_workbook(f,read_only=False,data_only=True)
ff=openpyxl.load_workbook(f,read_only=False,data_only=False)
check('seven_expected_sheets',v.sheetnames==['Resumen_privado','Cohortes_MU','Identidad_20','Cierres_observados','Matriculas_20','MU_anual_20','Fuentes'])
check('all_six_detail_tables_and_filters',sum(len(s.tables) for s in ff)==6 and all(t.autoFilter is not None for s in ff for t in s.tables.values()))
check('fixed_person_counts',Counter(v['Cohortes_MU'].cell(r,2).value for r in range(7,v['Cohortes_MU'].max_row+1))=={2024:558,2025:1150})
check('no_duplicate_person_rows',len({v['Cohortes_MU'].cell(r,1).value for r in range(7,1715)})==1708)
check('no_repeated_original_identity_within_cohort',len({(row[1],row[2],row[3],row[4]) for row in d['people']})==1708)
check('one_person_per_source_observation',len({(row[19],row[20],row[21]) for row in d['observations']})==len(d['observations']))
check('no_duplicate_full_enrolment_key_in_three_focus_snapshots',all(len({(row[3],row[4],row[6],row[7]) for row in d['observations'] if row[1]==label and row[24]==1})==15 for label in ['10246','11998','12112']))
for name,key in [('Cohortes_MU','people'),('Identidad_20','identity'),('Cierres_observados','closures'),('Matriculas_20','observations'),('MU_anual_20','annual20')]:
 check(name+'_all_source_rows_preserved',v[name].max_row-6==len(d[key]))
 # Every input field must match the private read-only source extraction. Formula-owned cells are checked separately.
 skip={'Identidad_20':{10,11}}.get(name,set())
 check(name+'_literal_inputs_exact',all(v[name].cell(ri,ci).value in (None,'') if value=='' else v[name].cell(ri,ci).value==value for ri,row in enumerate(d[key],7) for ci,value in enumerate(row,1) if ci not in skip))
for name,cols in [('Cohortes_MU',[3,4,5,9,10,11,12,15,16]),('Identidad_20',[3,4,5,6,7,8,9]),('Cierres_observados',[4,5,6]),('Matriculas_20',[3,4,5]),('MU_anual_20',[3,4,5,6,7,8,9,12])]:
 check(name+'_identifiers_stored_as_text',all(isinstance(v[name].cell(r,c).value,str) and v[name].cell(r,c).number_format=='@' for r in range(7,v[name].max_row+1) for c in cols if v[name].cell(r,c).value not in (None,'')))
actual=[[v['Resumen_privado'].cell(r,c).value for c in range(3,7)] for r in range(7,11)]
expected=[[x['denominator'],x['found'],'Sin campo' if x['vigente'] is None else x['vigente'],x['rows']] for x in d['control']]
check('all_four_closure_formulas_match_direct_counts',actual==expected)
check('all_four_rates_pending_E',all(v['Resumen_privado'].cell(r,9).value=='Pendiente' for r in range(7,11)))
check('20_reconciliation_formula_caches',[v['Resumen_privado'].cell(15,c).value for c in range(2,6)]==[20,18,2,19])
check('14_people_all_matriculas_formula_caches',[[v['Resumen_privado'].cell(r,c).value for c in range(2,6)] for r in range(18,21)]==[[14,15,13,1],[14,15,14,0],[14,15,14,0]])
errors=[];missing=[];nf=0
for s in ff:
 for row in s:
  for c in row:
   if c.data_type=='f':
    nf+=1;cc=v[s.title][c.coordinate]
    if cc.value is None:missing.append((s.title,c.coordinate))
    if cc.data_type=='e':errors.append((s.title,c.coordinate))
check('all_formula_caches_available',not missing)
check('zero_cached_formula_errors',not errors)
check('no_identity_unexpected_columns',not any(any(k in str(c.value or '').upper() for k in ['FECH_NAC','FECHANACIMIENTO','NOMBRE COMPLETO','PRIMER_APELLIDO','SEGUNDO_APELLIDO','MRUN']) for s in ff for row in s.iter_rows(min_row=6,max_row=6) for c in row))
privateids={str(x) for row in d['people'] for x in [row[3]] if len(str(x))>=6}
privateids|={str(x) for row in d['identity'] for x in [row[3],row[5],row[7],row[8]] if x and x!='Pendiente' and len(str(x))>=6}
agg=OLD/'RETENCION_INTERMEDIA_IPSS_REVISION_20261021_133221.xlsx'
desktop=Path('/Users/alexi/Desktop')/agg.name
check('aggregate_and_desktop_identical_verified_hash',sha(agg)==sha(desktop)=='66e7cc11a0206793504e4eb275d8585e070413067df6f20b9fde234d3daaa54c')
check('scenario80_sheet_unchanged',zipfile.ZipFile(agg).testzip() is None) # Whole-package unchanged hash is stronger than a sheet comparison.
aw=openpyxl.load_workbook(agg,read_only=True,data_only=False)
publicvals=[str(c.value) for s in aw for row in s for c in row if c.value is not None and c.data_type!='f']
private_pattern=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(i) for i in sorted(privateids,key=len,reverse=True))+r')(?![A-Za-z0-9])')
check('aggregate_contains_no_known_individual_identifiers',not any(private_pattern.search(value) for value in publicvals))
aw.close()
check('all_75_used_sources_hash_unchanged',all(sha(s['path'])==s['sha256'] for s in d['sources']))
state={}
for label,path in [('avance',R),('caracterizacion',Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN'))]:
 state[label]={'branch':subprocess.check_output(['git','branch','--show-current'],cwd=path,text=True).strip(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip(),'status_short':subprocess.check_output(['git','status','--short'],cwd=path,text=True),'remote':subprocess.check_output(['git','remote','get-url','origin'],cwd=path,text=True).strip()}
 (O/'soporte'/f'git_{label}_despues.txt').write_text(state[label]['status_short'])
 check(label+'_status_unchanged',state[label]['status_short']==(O/'soporte'/f'git_{label}_antes.txt').read_text())
check('avance_branch_and_HEAD_unchanged',state['avance']['branch']=='feature/ire-2026' and state['avance']['HEAD']=='80ca13a5a249a1a2bd53a699f5f73689b1f53040')
check('caracterizacion_HEAD_unchanged',state['caracterizacion']['HEAD']=='aba337784ccde0537fc21b2977b351170ed335e8')
result={'dictamen':'OK_CON_PENDIENTES_E','checks':checks,'controls_passed':len(checks),'new_private_formulas_with_cache':nf,'formula_errors':len(errors),'missing_caches':len(missing),'private_sha256':sha(f),'private_path':str(f),'aggregate_sha256':sha(agg),'aggregate_path':str(agg),'desktop_path':str(desktop),'closure_counts':actual,'git':state,'limits':['Artifact Tool; no apertura ni recálculo certificado en Excel nativo.','Suite general de reglas previa limitada por unidecode ausente; no se declara suite completa aprobada.','Cuatro tasas intermedias pendientes E; dos CODCLI sin correspondencia explícita.'],'no_commit_push_merge_PR':True}
(O/'QA_ENTREGA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
v.close();ff.close()
print(json.dumps({k:result[k] for k in ['dictamen','controls_passed','new_private_formulas_with_cache','formula_errors','missing_caches','private_sha256','closure_counts','no_commit_push_merge_PR']},ensure_ascii=False,indent=2))
