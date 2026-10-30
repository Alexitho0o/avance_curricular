"""Documenta el resultado de D10 y verifica el alcance de la publicación."""
import json
import re
import sqlite3
import subprocess
from pathlib import Path
from construir_v22 import ROOT,OUT,PRIVATE,D,OLD,DATA,load,dump,sha

def table(columns,rows):
    return '\n'.join(['| '+' | '.join(columns)+' |','|'+'---|'*len(columns)]+['| '+' | '.join(str(v) for v in row)+' |' for row in rows])
def rel(p):return str(p.relative_to(ROOT))
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
def main():
    assert git('rev-parse','HEAD')=='b2ebab08b09c529ddab8341ea882cf40406f16ad' and not git('diff','--cached','--name-only')
    qa=load(OUT/'QA_ACTIVACION.json');active=load(DATA/'activo.json')
    assert qa['estado']=='PASS' and active['descriptor']==rel(D/'descriptor.json') and sha(D/'descriptor.json')==active['sha256']
    for name in ('v21','ensayo_v22','puntero_real_v22'):
        assert all(x['delta_pp']==0 and [x['numerador'],x['denominador']]==x['referencia'] for x in qa[name]['tasas'].values())
    archive=DATA/'archivo_v21_h014'
    old=load(OLD);v20=load(ROOT/old['ACTIVO_ANTERIOR']['descriptor'])
    assert sha(OLD)==load(archive/'activo.json')['sha256'] and sha(old['base_privada']['ruta'])==old['base_privada']['sha256']
    assert sha(ROOT/old['ACTIVO_ANTERIOR']['descriptor'])==old['ACTIVO_ANTERIOR']['sha256'] and sha(v20['base_privada']['ruta'])==v20['base_privada']['sha256']
    (archive/'ARCHIVO_V21.md').write_text(f'# Archivo de v21 · H014\n\nEl puntero archivado conserva los bytes del activo H013. SHA-256 del puntero `{sha(archive/"activo.json")}`, del descriptor `{sha(OLD)}` y de la base privada `{old["base_privada"]["sha256"]}`. La selección operativa se obtiene del puntero activo del proyecto.\n')
    c=load(OUT/'COBERTURA.json');observed=load(OUT/'CONTROL_CASOS_ESPERADOS.json');hist=sum(x['n'] for x in c['historico']);ee=sum(x['n'] for x in c['residual'])
    assert hist==3049 and sum(x['n'] for x in c['posiciones99'])==99 and ee==59 and sum(x['n'] for x in c['revision_59'])==59
    assert sum(x['contextos'] for x in observed)==29 and not any(x['control_D10']=='OFERTA_AÑO_T1' for x in c['revision_59'])
    req={
        'CODIGO_MU_PLAN_AUSENTE_OFERTA_ANUAL':'IIND20251: aportar una línea MU del primer T1 posterior individual atribuible al mismo expediente y plan, con código de sede/jornada y año fuente. En la MU 2026 disponible no se localizan las personas de estos 24 contextos.',
        'T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO':'Para tres IECSREOL20211 falta un T1 posterior atribuible. Para NCONREOL2019 y NTCCREOL2020 falta evidencia que concilie el tipo y duración de su plan con la versión regular de ocho semestres informada en 2022.',
        'MU_PLAN_MENOS_DE_TRES_PERSONAS':'Referencia documental unánime de al menos tres personas o primer T1 propio acreditado.',
        'MU_PLAN_NO_UNANIME':'Documento del expediente que distinga las versiones observadas del plan.',
        'PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO':'Calendario UMAS que defina 4/5 para los tres contextos semestrales y tres trimestrales.',
        'PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS':'T1 único del expediente/plan con sede y jornada efectivas del cambio.',
        'SIN_CODIGO_ANUAL_COMPATIBLE':'Equivalencia formal del plan, sede, jornada y duración con la versión de oferta.',
        'SIN_FAMILIA_H002_U_OFERTA_ANUAL':'Evidencia anual que identifique familia y código ofertado.'}
    refined=[]
    for z in load(OUT/'RESIDUAL.json'):
        reason=z['motivo']
        if reason in ('CODIGO_MU_PLAN_AUSENTE_OFERTA_ANUAL','T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO'):
            resolved={r['control_D10'] for r in observed if r['plan']==z['plan'] and r['anio']==z['anio'] and r['motivo_anterior']==reason}
            assert len(resolved)==1
            reason=resolved.pop()
        refined.append(z|{'motivo_h013':z['motivo'],'motivo':reason})
    dump(OUT/'RESIDUAL_E_ACTUAL.json',refined)
    req['SIN_T1_POSTERIOR_MISMO_EXPEDIENTE_PLAN']='Aportar el primer T1 individual del mismo expediente y plan. Incluye 24 IIND20251 sin fila MU 2026 y tres IECSREOL20211 sin T1 posterior localizado.'
    req['TIPO_O_DURACION_NO_COINCIDE']='Conciliar la versión regular de ocho semestres informada en 2022 con el plan de continuidad de cuatro semestres de NCONREOL2019 o cinco de NTCCREOL2020.'
    motivos=sorted({z['motivo'] for z in refined})
    rows=[(m,sum(z['n'] for z in refined if z['motivo']==m),req[m]) for m in motivos]
    assert sum(n for _,n,_ in rows)==59
    (OUT/'SOLICITUD_UMAS_RESIDUAL.md').write_text('# Solicitud UMAS · borrador sin enviar\n\nSe requieren respaldos para 59 contextos de seguimiento. Entregar primero catálogos y cronología por plan, sede, jornada y año. El detalle nominativo indispensable se recibe únicamente en carpeta restringida. RESIDUAL_E_ACTUAL.json desglosa las combinaciones pendientes. La oferta del año del T1 fuente rige para PRIMER_T1_POSTERIOR.\n\n'+table(['Motivo vigente','Contextos','Evidencia necesaria'],rows)+'\n')
    report=OUT/'INFORME_H014.md'
    report.write_text(f'''# H014 · v22 activa

**D · Alexi, 30-10-2026.** En PRIMER_T1_POSTERIOR el año de oferta que valida el código es el año de ese primer T1. Exigir el mismo expediente y plan, sede, jornada, tipo y duración total coherentes. Sólo esa vía usa la marca OFERTA_AÑO_T1. Las atribuciones anteriores se conservaron sin reclasificación.

**B/C.** De los 59 contextos E revisados, cero cumplieron D10. El universo queda en 2.990/3.049 contextos respaldados y 99/99 posiciones. Los 24 IIND20251 sin línea individual MU en 2026 no pueden usar por esta vía la referencia grupal de 83 personas en I162S2C87J4V2. En los otros cinco casos, tres IECSREOL20211 carecen de primer T1 posterior atribuible en las fuentes y dos tienen un T1 en 2022 que falla el control de perfil. NCONREOL2019 tiene continuidad de cuatro semestres frente a C3J4V2 regular de ocho. NTCCREOL2020 tiene continuidad de cinco semestres frente a C46J4V3 regular de ocho. CONTROL_CASOS_ESPERADOS.json conserva año, código, perfil y conteos. No se atribuye la referencia de otra persona.

## Residual E

{table(['Motivo vigente','Contextos','Requisito actual'],rows)}

## Control del puntero real

{table(['Indicador','Numerador','Denominador','Diferencia (pp)'],[(k,v['numerador'],v['denominador'],'0,00') for k,v in qa['puntero_real_v22']['tasas'].items()])}

H001 se recalculó sobre su MU y catálogo gobernados. R19 usa las banderas de la foto aprobada. Los totales se reagruparon por contexto de cada puntero, incluyendo los casos sin enlace y con múltiples contextos. El ingreso T2 usa la fuente de matrículas y renuncias agregadas por área. QA_ACTIVACION.json compara v21, el ensayo aislado v22 y el puntero v22 real.

Las tres interfaces coincidieron en {qa['consumidores']['consultas_por_consumidor']} consultas cada una. MU2027 probó 4.105 antiguos. Pasaron las pruebas de paridad H002 y MU2027. Se reprodujeron las asignaciones, base SQLite y salidas agregadas por hash antes de activar. Reproducción: ejecutar construir_v22.py con v21 activa, luego activar_v22.py y cerrar_h014.py. El constructor protege la base activa contra sobrescritura.

El puntero activo selecciona `{active['descriptor']}` con SHA-256 `{active['sha256']}`. La capa PROMEDIOS conserva sus bytes. La base v22, sus asignaciones privadas y la tabla asignaciones_v22 materializan esta edición. Las bases v20 y v21 se verificaron por sus hashes originales.
''')
    mp=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.json';m=load(mp);r=next(x for x in m['resultados'] if x['id']=='R29')
    r.update(resultado_clave='ACTIVA v22 H014. 2.990 de 3.049 contextos y 99 de 99 posiciones respaldadas. D10 verifica oferta del primer T1 individual posterior. Cero altas, 59 E. R01–R04 y R19 con 0,00 pp por recálculo.',archivo=rel(report),sha256=sha(report),script_productor=rel(OUT/'activar_v22.py'),commit='PUBLICACION_H014; base b2ebab0',hoja_o_seccion='D10, residual y control del puntero real',limites='La referencia del plan no acredita un primer T1 del mismo expediente. D7 conserva el riesgo H013. v20 y v21 archivadas.')
    mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    md=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.md';line='| '+' | '.join([r['id']+' · '+r['pregunta']]+[r[k] for k in ['resultado_clave','archivo','script_productor','commit','sha256','clase','fecha_resultado','no_recalcular_salvo']])+' |'
    md.write_text('\n'.join(line if l.startswith('| R29 ·') else l for l in md.read_text().splitlines())+'\n')
    paths=sorted({rel(f) for f in [*OUT.iterdir(),*D.iterdir(),*archive.iterdir()] if f.is_file()}|{rel(mp),rel(md),rel(DATA/'activo.json'),rel(OUT/'LISTA_PUBLICACION.json'),rel(OUT/'QA_FINAL.json')})
    dump(OUT/'LISTA_PUBLICACION.json',{'rutas':paths,'base':'b2ebab0'})
    state=load(PRIVATE.parent/'h010_20261030/ESTADO_INICIAL.json');assert all(sha(ROOT/f)==h for f,h in state['ajenos'].items()) and all(s in git('status','--porcelain').splitlines() for s in state['status_ajenos'].splitlines())
    dump(OUT/'QA_FINAL.json',{'estado':'PASS_ACTIVA_V22','pruebas_D10':6,'tasas_pp':0.0,'archivos_reproducidos':5,'reproduccion_sha256':(PRIVATE/'reproduccion.sha256').read_text().splitlines(),'puntero':active,'residual_E':ee,'altas':0,'v20_v21_hash_intacto':True,'25_ajenos_intactos':True,'hallazgos_privacidad':[]})
    db=sqlite3.connect(Path(old['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
    ids={str(v) for row in db.execute('select persona,codcli from observaciones') for v in row if v is not None};db.close();ids.update({v.split('-')[0] for v in ids if '-' in v})
    pattern=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(x) for x in sorted(ids) if len(x)>=6)+r')(?!\w)')
    generic=re.compile(r'(?<!\w)(?:\d{7,8}-[0-9Kk]|\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]|\+56\s*[29]\s*\d{4}\s*\d{4}|[29]\d{8})(?!\w)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
    for f in paths:
        assert Path(f).suffix in ('.md','.json','.py')
        for l in (ROOT/f).read_text().splitlines():assert not pattern.search(l) and not generic.search(l),f
    print('PASS',len(paths),'rutas')
if __name__=='__main__':main()
