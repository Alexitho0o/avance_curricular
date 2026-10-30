"""Comprueba reproducibilidad, actualiza R30 y prepara el manifiesto agregado H011."""
import collections as C
import json
import re
import sqlite3
import subprocess
from pathlib import Path
import os
import sys
from aplicar_h011 import OUT,ROOT,CAT,OLD,PRIVATE,sha,dump

load=lambda p:json.loads(Path(p).read_text())
git=lambda *a:subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
rel=lambda f:str(f.relative_to(ROOT))
def read_levels(rows):
    return {r['nivel_asignacion']:r['n'] for r in rows}
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'---|'*len(headers)]+['| '+' | '.join(str(v) for v in row)+' |' for row in rows])
requirements={
 'AMBIGUEDAD_ANUAL_PERSISTENTE':'Distinguir las versiones anuales compatibles con respaldo de expediente/plan.',
 'PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO':'Definición y decisión específica de período para esos tres contextos semestrales y tres trimestrales.',
 'PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS':'Acreditar versión única y sede/jornada del primer T1 de ese expediente.',
 'SIN_CALCE_DURACION_TOTAL_TIPO_MODALIDAD':'Corregir o acreditar perfil formal y duración total de la versión anual.',
 'SIN_CODIGO_ANUAL_COMPATIBLE':'Acreditar un código anual compatible con el plan.',
 'SIN_FAMILIA_H002_U_OFERTA_ANUAL':'Acreditar familia exacta y presencia en oferta del año.',
 'SIN_VIGENCIA_1_COMPATIBLE':'Versión VIGENCIA 1 del tipo compatible o decisión explícita para la excepción.',
 'T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO':'Acreditar equivalencia del código del T1 con el tipo/duración y oferta del año del contexto.',
 'VARIAS_VIGENCIA_1_COMPATIBLES':'Documento que determine cuál de varias versiones con VIGENCIA 1 corresponde al expediente.',
}
def main():
    expected='fc9d401586ef2dcfd53c7270a95cb774122e34b1'
    assert git('rev-parse','HEAD')==expected and git('branch','--show-current')=='feature/ire-2026' and not git('diff','--cached','--name-only')
    run=lambda args: subprocess.run([sys.executable,*args],check=True,env=os.environ|{'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
    outputs=[CAT/'TIPO_PLAN_v3_CANDIDATO.json',OUT/'COBERTURA_H011.json',OUT/'RESIDUAL_H011.json',OUT/'FUENTES_H011.json',PRIVATE/'ASIGNACIONES_H011_PRIVADAS.json']
    before_hash={p:sha(p) for p in outputs}
    run([str(OUT/'aplicar_h011.py')])
    assert before_hash=={p:sha(p) for p in outputs}
    tests=run(['-m','unittest','discover','-s',str(OUT),'-p','test_h011.py'])
    assert 'Ran 5 tests' in tests.stderr
    cat=load(outputs[0])['perfiles'];data=load(outputs[1]);h=data['historico'];p99=data['posiciones99'];ee=read_levels(h['despues'])['E']
    assert sum(read_levels(h['despues']).values())==3049 and sum(read_levels(p99['despues']).values())==99 and read_levels(h['antes'])['E']==964
    assert sum(r['n'] for r in h['altas_por_via'])==964-ee and p99['antes']==p99['despues']
    evidence=load(OUT/'EVIDENCIA_PASO1_REOL.json');plans=sorted(r['plan'] for r in evidence['listado_UMAS'])
    profiles_rows=[];annual=[]
    for plan in plans:
        rr=[x for x in cat if x['plan']==plan]
        assert rr
        choices=set();opts=set()
        for x in rr:
            for code,v in x['opciones'].items():
                opts.add((code,v['total'],v['tipo']))
            compatible=x['compatibles']
            choice=x['motivo_E'] or (compatible[0] if len(compatible)==1 else 'E versión múltiple: '+', '.join(compatible))
            choices.add(choice)
            short=lambda code:code.replace('I162S2','')
            listing=', '.join(f"{short(code)} ({v['total']} sem., {v['tipo']})" for code,v in sorted(x['opciones'].items()))
            annual.append((plan,x['carrera'],x['anio'],listing or 'Sin oferta',choice))
        first=rr[0]
        profiles_rows.append((plan,first['nivel_maximo'],first['semestres_exactos'],first['semestres_convertidos'],', '.join(f"{short(c)} ({d}, {t})" for c,d,t in sorted(opts)), ' / '.join(sorted(choices))))
    (OUT/'TABLA_22_REOL.md').write_text('# Perfiles de los 22 planes REOL\n\nDuración en semestres. El código abreviado omite I162S2. Las opciones que comparten perfil se mantienen visibles para resolver por T1 o por vigencia cuando la regla lo permite. Una compatibilidad de catálogo por sí sola no adjudica un contexto.\n\n'+table(['Plan','NIVEL máximo','Semestres exactos','Entero','Opciones observadas (duración total, tipo)','Elección o E según año'],profiles_rows)+'\n\n## Detalle anual\n\n'+table(['Plan','Carrera','Año','Oferta anual','Elección o E'],annual)+'\n')
    residualrows=[(z['motivo'],z['n'],requirements[z['motivo']]) for z in h['residual']]
    dump(OUT/'REQUISITOS_E_H011.json',{r[0]:{'contextos_historicos':r[1],'requisito':r[2]} for r in residualrows})
    versions=load(ROOT/'data/diccionario_sies_seguimiento/activo.json')
    active=load(ROOT/versions['descriptor'])
    qa_h010=load(OLD/'FUENTES.json')['fuentes']
    unchanged={v['ruta']:sha(v['ruta'])==v['sha256'] for v in qa_h010 if Path(v['ruta']).name in ['RETENCION_PRIMER_ANIO_AGREGADO.json','REGLA.json','activo.json']}
    assert len(unchanged)>=3 and all(unchanged.values()) and sha(active['base_privada']['ruta'])==active['base_privada']['sha256']
    baseline=load(PRIVATE.parent/'h010_20261030/ESTADO_INICIAL.json')
    assert all(sha(ROOT/p)==v for p,v in baseline['ajenos'].items())
    status=git('status','--porcelain').splitlines();assert all(s in status for s in baseline['status_ajenos'].splitlines())
    report=OUT/'INFORME_H011.md'
    report.write_text(f'''# H011 · código de seguimiento por duración total y T1

**CANDIDATA.** Alexi retiró la premisa que atribuía un tipo de plan a RE o CO. Son sedes. Para los 22 planes REOL del residual, H002 acredita modalidad no presencial. El régimen S/A del listado corresponde a la asignatura. El plan ADMP20251 tiene 65 filas S en el listado y actividad trimestral en PROMEDIOS. El Paso 1c queda acreditado por esa diferencia de grano. La distribución literal de 277 filas CO dejó de intervenir en el control.

**D5.** Primero se consulta el perfil v2 por carrera, plan y sede. Para un perfil faltante se toma el máximo NIVEL por CODPESTUD y el régimen observado en PROMEDIOS. En bimestral se aplica 2/5 por nivel, en semestral se conserva el nivel y en trimestral se aplica ceil(2n/3) de docs/SEGUIMIENTO_RUT_Y_CONVERSION_PERIODOS_20261023.md. La zona inclusiva de 0,1 alrededor de x,5 queda E. Se exige igualdad entera con DURACIÓN TOTAL anual. El código compatible aporta el tipo. Si dos perfiles de igual duración tienen tipos distintos, queda E. Los nombres y las sedes por sí solos no seleccionan el tipo.

**B/C.** TABLA_22_REOL.md contiene los 22 planes con candidatos por año, duración total, tipo y elección o E. El catálogo candidato está en data/paridad_codigo_sies/tipo_plan_h011_20261030/TIPO_PLAN_v3_CANDIDATO.json. El período nativo y la clasificación documental previa se conservan. La asignación individual candidata está únicamente en almacenamiento privado.

| Universo | Antes | Después | Residual E |
|---|---:|---:|---:|
| 3.049 contextos | 2.085 | {3049-ee:,} | {ee} |
| 99 posiciones | 99 | 99 | 0 |

{table(['Decisión de entrada','Nivel resultante','Nuevas'],[(r['via_h011'],r['nivel_asignacion'],r['n']) for r in h['altas_por_via']])}

Cada alta se cuenta una vez. Las filas nativas 4/5 entran por D6, incluso cuando su código proviene del último T1. El nivel ARRASTRE_ULTIMO_T1 recoge esos casos y los antiguos de D4. Un T1 no compatible con la oferta del año queda E.

## Residual histórico

{table(['Motivo','Contextos','Requisito de cierre'],residualrows)}

El residual es {100*ee/3049:.2f} % frente a la meta ≤0,1 %. Los requisitos de cada grupo están en REQUISITOS_E_H011.json y el desglose por plan, año, período, sede y jornada en RESIDUAL_H011.json. La revisión de 99 posiciones mantiene residual cero.

## Controles

R01–R04 y R19 tienen 0,00 pp de cambio por conservación de las fuentes. Se verificaron por SHA-256. v20 activo y v21 candidata. La reproducción y la privacidad se documentan en QA_H011.json. FUENTES_H011.json fija las entradas, incluida la conversión trimestral. La reproducción usa aplicar_h011.py seguido de cerrar_h011.py.
'''.replace(f'{3049-ee:,}',f'{3049-ee:,}'.replace(',','.')).replace(f'{100*ee/3049:.2f} %',f'{100*ee/3049:.2f}'.replace('.',',')+' %'))
    mp=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.json';m=load(mp)
    row={'id':'R30','pregunta':'¿Qué código candidato de seguimiento se puede respaldar con el perfil anual, el período bimestral y el último T1?','resultado_clave':f'CANDIDATA H011: {3049-ee} de 3.049 contextos respaldados, {ee} E. 99 de 99 posiciones respaldadas. R01–R04/R19 0,00 pp por conservación.','archivo':rel(report),'hoja_o_seccion':'Cobertura y residual histórico','script_productor':rel(OUT/'aplicar_h011.py'),'commit':'PUBLICACION_H011; base fc9d401','sha256':sha(report),'clase':'D decisiones; B/C fuentes y aplicación; E pendientes','fecha_resultado':'2026-10-30','no_recalcular_salvo':'Nueva evidencia anual, de perfil o de expediente que resuelva los motivos E, o decisión expresa de Alexi.','limites':'La v21 es candidata. El catálogo v3 propuesto se separa del perfil v2 y de H002m.'}
    m['resultados']=[x for x in m['resultados'] if x['id']!='R30']+[row];mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    md=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.md';s='\n'.join(l for l in md.read_text().splitlines() if not l.startswith('| R30 ·'))+'\n'
    line='| '+' | '.join([row['id']+' · '+row['pregunta']]+[row[k] for k in ['resultado_clave','archivo','script_productor','commit','sha256','clase','fecha_resultado','no_recalcular_salvo']])+' |'
    s=s.replace('## Mapa (29 resultados)','## Mapa (30 resultados)').replace('\n## Límites por resultado','\n'+line+'\n\n## Límites por resultado')
    md.write_text(s)
    paths=sorted({rel(p) for p in OUT.iterdir() if p.is_file()} | {rel(outputs[0]),rel(mp),rel(md),rel(OUT/'QA_H011.json'),rel(OUT/'LISTA_PUBLICACION.json')})
    dump(OUT/'LISTA_PUBLICACION.json',{'rutas':paths,'estado':'CANDIDATA'})
    qa={'estado':'PASS_QA_CON_RESIDUALES_E','meta_residual_alcanzada':ee/3049<=0.001,'pruebas_conversion':5,'reproduccion_sha256':{p.name:h for p,h in before_hash.items()},'altas_sobre_3049':964-ee,'contextos_E':ee,'R01_R04_R19_delta_pp':0.0,'fuentes_indicadores_intactas':unchanged,'v20_intacto':True,'25_ajenos_intactos':True,'hallazgos_identificadores':[]}
    dump(OUT/'QA_H011.json',qa)
    db=sqlite3.connect(Path(active['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
    ids={str(v) for row in db.execute('select persona,codcli from observaciones') for v in row if v is not None};db.close()
    ids.update({s.split('-')[0] for s in ids if '-' in s})
    rx=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(v) for v in sorted(ids) if len(v)>=6)+r')(?!\w)')
    contact=re.compile(r'(?<!\w)(?:\d{7,8}-[0-9Kk]|\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]|\+56\s*[29]\s*\d{4}\s*\d{4}|[29]\d{8})(?!\w)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
    for path in paths:
        assert Path(path).suffix in ('.json','.py','.md')
        for line in (ROOT/path).read_text().splitlines():
            assert not rx.search(line) and not contact.search(line),'Hallazgo privado: '+path
    print('PASS',len(paths),'archivos;',ee,'E')
if __name__=='__main__':main()
