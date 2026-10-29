#!/usr/bin/env python3
"""QA de promoción H002e: paridad íntegra de filas y preservación histórica vía Git."""
from pathlib import Path
from collections import Counter
import csv
import io
import hashlib
import json
import re
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from resolver_planes_h002c import sha,dump,load,rows

MODIFIED={
    'data/paridad_codigo_sies/20261029/FUENTES.json','data/paridad_codigo_sies/20261029/MANIFEST.json',
    'data/paridad_codigo_sies/20261029/README.md','data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json',
    'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.csv',
    'outputs/paridad_codigo_sies_20261029/construir_paridad.py',
    'outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.json','outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.md',
    'outputs/paridad_codigo_sies_20261029/QA.json','outputs/paridad_codigo_sies_20261029/RESOLUCIONES_POR_GRUPO.json',
    'manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/REGISTRO.json',
    'manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/README.md'}


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def old(base,path):return json.loads(git('show',base+':'+path))


def main():
    baseline=load('outputs/paridad_codigo_sies_20261029/ESTADO_INICIAL_H002E.json');base=baseline['HEAD']
    before=old(base,'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas']
    current=load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json');after=current['filas']
    previous={(x['anio'],x['codigo_unico']):x for x in before};now={(x['anio'],x['codigo_unico']):x for x in after}
    d=load('data/paridad_codigo_sies/20261029/DECISIONES_APROBADAS_v2.json')
    decisions=load('outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.json');groups=load('outputs/paridad_codigo_sies_20261029/RESOLUCIONES_POR_GRUPO.json')
    targets={x['grupo'] for x in d['correspondencias']+d['planes_historicos']}|{d['pendiente_CADMP']['grupo']}
    c35={x['codigo_unico'] for x in d['codigos_historicos']}
    allowed={k for k,v in previous.items() if k[0]==2027 and (k[1] in c35 or any(g['grupo'] in targets for g in v['resoluciones_grupo']))}
    delta={k for k,v in now.items() if v!=previous[k]}
    checks={}
    checks['rama_HEAD']=git('rev-parse','HEAD').decode().strip()==base and git('branch','--show-current').decode().strip()==baseline['rama']
    checks['mismos_267_codigos_106_161']=set(previous)==set(now) and Counter(r['anio'] for r in after)==Counter({2026:106,2027:161})
    checks['solo_20_filas_decisiones_1_a_4']=delta==allowed and len(delta)==20
    fields={'estado_antes_H002e','decision_H002e','evidencia','estado','clase','version_para_nuevos_2027','motivo',
        'ultima_matricula_publica','resoluciones_grupo','decisiones_por_grupo_H002e','correspondencias_aprobadas_H002e',
        'candidatos_internos','estado_plan_por_cohorte','indicio_H002e'}
    changes=[]
    for key in sorted(delta):
        aa,bb=previous[key],now[key]
        ff={f for f in set(aa)|set(bb) if aa.get(f)!=bb.get(f)}
        changes.append({'anio':key[0],'codigo_unico':key[1],'estado_antes':aa['estado'],'estado_despues':bb['estado'],'campos_cambiados':sorted(ff)})
    checks['solo_campos_autorizados']=all(set(x['campos_cambiados'])<=fields for x in changes)
    checks['2026_integro']=all(now[k]==v for k,v in previous.items() if k[0]==2026)
    checks['37_pendientes_integros']=all(now[(2027,c)]==previous[(2027,c)] for c in d['37_pendientes_sin_cambio'])
    checks['5_D_codigo_grupo_y_fuente']=all(now[(2027,x['codigo_unico'])]['estado']=='APROBADA_D_2027' and
        now[(2027,x['codigo_unico'])]['clase']=='D' and now[(2027,x['codigo_unico'])]['decision_H002e']['fuente']=='Alexi, 29-10-2026' and
        any(z['grupo']==x['grupo'] and z['codigo_unico']==x['codigo_unico'] for z in now[(2027,x['codigo_unico'])]['correspondencias_aprobadas_H002e']) for x in d['correspondencias'])
    checks['6_D_H002b_intactas']=all(now[k]==v for k,v in previous.items() if v['estado']=='APROBADA_D_2027')
    hh=[g for g in groups if g.get('estado_paridad_2027')=='PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES']
    checks['6_grupos_historicos_D_sin_version']=len(hh)==6 and all(g['clase_paridad_2027']=='D' and g['ambiguedad_historica']['clase']=='E' and g['ambiguedad_historica']['version_asignada'] is None for g in hh)
    original_groups={g['grupo']:g for g in old(base,'outputs/paridad_codigo_sies_20261029/RESOLUCIONES_POR_GRUPO.json')}
    checks['otros_123_grupos_intactos']=all(g==original_groups[g['grupo']] for g in groups if g['grupo'] not in targets)
    checks['no_cierre_codigos_compartidos']=all(r['estado']!='PLAN_HISTORICO_SIN_ALUMNOS_VIGENTES' for r in after if r['anio']==2027)
    checks['CADMP_E_en_2_codigos']=len([r for r in after if r['anio']==2027 and r['estado']=='VERSION_MULTIPLE_E'])==2 and [g['codcarpr'] for g in decisions['version_multiple_E_por_grupo']]==['CADMP'] and all(now[(2027,c)]['indicio_H002e']['aprobada'] is False for c in ['I162S2C83J4V1','I162S2C83J4V2'])
    checks['6_C35_historicos']=all(now[(2027,c)]['estado']=='HISTORICO_SIN_MATRICULA_RECIENTE' and now[(2027,c)]['clase']=='D' for c in c35)
    checks['11_D_y_37_pendientes']=sum(r['anio']==2027 and r['estado']=='APROBADA_D_2027' for r in after)==11 and len(decisions['nuevo_2027_sin_plan_E'])==37
    checks['vigencia_literal_y_TAMD_no_nuevos']=all(r['vigencia_2027']==previous[(r['anio'],r['codigo_unico'])]['vigencia_2027'] and (r['vigencia_2027']!='2' or r['version_para_nuevos_2027']=='no') for r in after)
    with (ROOT/'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.csv').open() as f:
        csvrows=list(csv.DictReader(f,delimiter=';'))
    oldcsv=list(csv.DictReader(io.StringIO(git('show',base+':data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.csv').decode()),delimiter=';'))
    oldcells={(int(r['anio']),r['codigo_unico']):r for r in oldcsv}
    cells={(int(r['anio']),r['codigo_unico']):r for r in csvrows}
    checks['CSV_campos_previos_intactos_fuera_20_filas']=all(all(cells[k][f]==v for f,v in row.items()) for k,row in oldcells.items() if k not in allowed)
    checks['CSV_columnas_nuevas_vacias_fuera_20_filas']=all(all(not v for f,v in row.items() if f not in oldcells[k]) for k,row in cells.items() if k not in allowed)
    checks['CSV_JSON_sumas_estados']=len(csvrows)==267 and {(int(r['anio']),r['codigo_unico']):r['estado'] for r in csvrows}=={k:r['estado'] for k,r in now.items()} and all(Counter(r['estado'] for r in after if r['anio']==y)==Counter({k:v for k,v in current['conteos_por_anio_estado'][str(y)].items() if v}) for y in [2026,2027])
    checks['historial_decision_1_conservado']=sha(ROOT/d['decision_anterior_conservada']['ruta'])==d['decision_anterior_conservada']['sha256']
    manifest=load('data/paridad_codigo_sies/20261029/MANIFEST.json')
    checks['manifest_entradas_salidas_codigo']=all(sha(ROOT/x['ruta'])==x['sha256'] for x in manifest['entradas']) and all(sha(ROOT/p)==h for p,h in manifest['salidas'].items()) and sha(ROOT/manifest['generador']['ruta'])==manifest['generador']['sha256'] and all(sha(ROOT/p)==h for p,h in manifest['auxiliares_H002e'].items())
    checks['milestone_apunta_manifest']=load('manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/REGISTRO.json')['manifest_sha256']==sha(ROOT/'data/paridad_codigo_sies/20261029/MANIFEST.json')
    status=git('status','--porcelain').decode().splitlines()
    checks['24_ajenos_status']=all(s in status for s in baseline['status']) and len(baseline['status'])==24
    checks['24_ajenos_bytes']=all(sha(ROOT/x['ruta'])==x['sha256'] for x in baseline['ajenos'])
    checks['otros_archivos_H002_intactos']=all(sha(ROOT/p)==h for p,h in baseline['protegidos'].items() if p not in MODIFIED)
    changed=set(git('diff','--name-only').decode().splitlines())|set(git('diff','--cached','--name-only').decode().splitlines())
    checks['diff_solo_H002']=all(p in MODIFIED or (p.startswith(('outputs/paridad_codigo_sies_20261029/','data/paridad_codigo_sies/20261029/')) and p not in baseline['protegidos']) for p in changed)
    # Las referencias congeladas se verifican por sus bytes previos en Git cuando
    # la tabla/constructor vigente cambió de forma autorizada. No retocar hashes.
    def historical_valid(path,expected):
        p=Path(path);p=p if p.is_absolute() else ROOT/p
        if p.is_file() and sha(p)==expected:return True
        if p.is_relative_to(ROOT):
            try:return hashlib.sha256(git('show',base+':'+str(p.relative_to(ROOT)))).hexdigest()==expected
            except subprocess.CalledProcessError:return False
        return False
    historical_checks=[]
    for filename in ['MANIFEST_H002C.json','MANIFEST_H002D.json']:
        mm=load('outputs/paridad_codigo_sies_20261029/'+filename)
        historical_checks.append(all(historical_valid(x['ruta'],x['sha256']) for x in mm['fuentes']) and
            all(historical_valid(OUT/p,h) for p,h in mm['salidas'].items()) and all(historical_valid(ROOT/p,h) for p,h in mm['componentes'].items()))
    checks['antecedentes_C_D_por_commit_y_fuentes_intactos']=all(historical_checks)
    control=load('outputs/paridad_codigo_sies_20261029/CONTROL_VIGENTES_H002E.json');per=control['fuente']
    checks['Permanencia_fuente_intacta']=sha(per['ruta'])==per['sha256']
    cnt=Counter();wanted={(x['codcarpr'],x['sede'],x['jornada']) for x in control['grupos']}
    for _,row in rows(per['ruta'],'Worksheet'):
        key=(str(row.get('CARRERA_ALUM')).strip(),str(row.get('COD_SEDE')).strip(),str(row.get('JORNADA')).strip())
        if key in wanted:cnt[key+(str(row.get('ESTADO_ALUMNO')).strip(),)]+=1
    checks['cero_vigentes_y_IECIRE_titulado']=all(sum(n for k,n in cnt.items() if k[:3]==(x['codcarpr'],x['sede'],x['jornada']) and k[3].upper()=='VIGENTE')==0 for x in control['grupos']) and cnt[('IECIRE','RE','O','TITULADO')]==1
    obs=(OUT/'OBSERVACIONES_OFERTA_2027.md').read_text()
    checks['7_observaciones_y_manual_p28']=all(x['codigo_unico'] in obs for x in d['observaciones_oferta']) and 'página 28' in obs and len(d['observaciones_oferta'])==7
    tests=[]
    for p in sorted(OUT.glob('test_*.py')):
        run=subprocess.run([sys.executable,'-B',str(p)],cwd=ROOT,text=True,capture_output=True)
        tests.append({'archivo':p.name,'exit':run.returncode,'pruebas':sum(int(n) for n in re.findall(r'Ran (\d+) tests?',run.stderr)),
            'error':run.stderr[-1500:] if run.returncode else ''})
    checks['51_pruebas_H002']=sum(t['pruebas'] for t in tests)==51 and all(t['exit']==0 for t in tests)
    run=subprocess.run([sys.executable,'-B',str(OUT/'construir_paridad.py'),'--verificar'],cwd=ROOT,capture_output=True,text=True)
    checks['reproduccion_identica_por_hash']=run.returncode==0
    patterns={'RUT_DV':r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)',
        'email':r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','CODCLI':r'(?<!\w)(?:19|20)\d{2}[1-5][A-Z]{2,12}\d{3,}(?!\w)'}
    findings=[]
    folders=[ROOT/'data/paridad_codigo_sies/20261029',OUT,ROOT/'manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027']
    for folder in folders:
        for p in folder.iterdir():
            if not p.is_file():continue
            text=re.sub(r'\b(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40})\b','HASH',p.read_text())
            for label,pattern in patterns.items():
                if re.search(pattern,text):findings.append({'ruta':str(p.relative_to(ROOT)),'patron':label})
    checks['privacidad_sin_hallazgos']=not findings
    (OUT/'DIFF_H002E.json').write_text(dump({'clase':'C','commit_base':base,'filas_modificadas':changes,'total':len(changes),
        '2026_intacto':checks['2026_integro'],'37_intactas':checks['37_pendientes_integros'],'solo_campos_autorizados':checks['solo_campos_autorizados'],
        'nota_CSV':'La cabecera incorpora metadatos H002e. Fuera de las veinte filas, todos los campos previos son idénticos y las columnas nuevas están vacías.'}))
    result={'hito':'H002e','clase':'C','estado':'PASS_CON_PENDIENTES_E' if all(checks.values()) else 'FAIL',
        'controles':checks,'pruebas':tests,'hallazgos_privacidad':findings,'reproduccion_error':run.stderr[-1800:] if run.returncode else '',
        'nota':'La decisión D no acredita aceptación SIES ni atribuciones personales. Seis grupos históricos no son seis códigos cerrados.'}
    (OUT/'QA_H002E.json').write_text(dump(result));print(dump(result))
    return 0 if all(checks.values()) else 1


if __name__=='__main__':raise SystemExit(main())
