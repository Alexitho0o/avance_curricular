"""Reproduce el resultado, registra el residual con requisito y prepara la publicación."""
import os
import re
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from resolver import ROOT,OUT,OLD,P,dump,sha

load=lambda p:json.loads(Path(p).read_text())
rel=lambda p:str(p.relative_to(ROOT))
git=lambda *a:subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def table(h,rows):
    return '\n'.join(['| '+' | '.join(h)+' |','|'+'---|'*len(h)]+['| '+' | '.join(str(v) for v in row)+' |' for row in rows])
def decimal(v,n=5):return f'{v:.{n}f}'.replace('.',',')

requirements={
'D7_NO_SUPERA_VALIDACION_UNANIME':'El grupo es unánime, pero el método no pasa el umbral. Hace falta evidencia documental del expediente o una nueva decisión expresamente validada.',
'D7_NO_SUPERA_VALIDACION_NO_UNANIME':'El grupo contiene distintas versiones. La distribución por plan/año figura en el detalle. Hace falta evidencia que discrimine dentro del grupo.',
'D7_NO_SUPERA_VALIDACION_MENOS_DE_TRES_PERSONAS':'Se necesitan tres personas distintas como mínimo en el año de referencia y superar el umbral de la regla.',
'PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO':'Definición UMAS de 4/5 para los tres contextos semestrales y tres trimestrales pendientes.',
'PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS':'T1 acreditado del expediente y plan, unívoco y con dimensiones compatibles.',
'SIN_CALCE_DURACION_TOTAL_TIPO_MODALIDAD':'Perfil formal o versión anual compatible en duración total, tipo y modalidad.',
'SIN_CODIGO_ANUAL_COMPATIBLE':'Código anual compatible para el plan.',
'SIN_FAMILIA_H002_U_OFERTA_ANUAL':'Familia acreditada y oferta del año correspondiente.',
'T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO':'Evidencia que explique el T1 frente a la oferta y al perfil anual.',
}
def main():
    assert git('rev-parse','HEAD')=='dd34eaf77560fd84e5367782859b18db6c24f473' and not git('diff','--cached','--name-only')
    files=[OUT/n for n in ['CORRECCION_FAMILIA_H002_CANDIDATA.json','VALIDACION_D7.json','COBERTURA_H012.json','RESIDUAL_H012.json','FUENTES_H012.json']]+[P/'ASIGNACIONES_H012_PRIVADAS.json']
    checks={p:sha(p) for p in files};env=os.environ|{'PYTHONDONTWRITEBYTECODE':'1'}
    subprocess.run([sys.executable,str(OUT/'resolver.py')],env=env,check=True,capture_output=True)
    assert all(sha(p)==v for p,v in checks.items())
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(OUT),'-p','test_h012.py'],env=env,capture_output=True,text=True,check=True)
    assert 'Ran 5 tests' in tests.stderr
    cov=load(files[2]);val=load(files[1]);control=load(files[0]);ee=cov['despues_E'];names={z['plan']:z for z in control}
    prev=load(P.parent/'h011_20261030/ASIGNACIONES_H011_PRIVADAS.json');after=load(files[-1])
    aa=load(ROOT/'data/diccionario_sies_seguimiento/activo.json');d=load(ROOT/aa['descriptor'])
    assert sha(ROOT/aa['descriptor'])==aa['sha256'] and sha(d['base_privada']['ruta'])==d['base_privada']['sha256']
    assert len(prev)==len(after) and all(a==b for a,b in zip(prev,after) if a['nivel_asignacion']!='E')
    positions=load(P.parent/'h010_20261030/POSICIONES_99_H010B_PRIVADAS.json')
    index={r['observacion_id']:r for r in after};assert len(positions)==99 and all(index[z['observacion_id']]==z for z in positions)
    assert not val['D7_habilitada'] and not any(z['nivel_asignacion']=='VERSION_POR_MU_DEL_PLAN' for z in after)
    indicators={x['ruta']:x['sha256'] for x in load(ROOT/'outputs/regla_t1_h010_20261030/FUENTES.json')['fuentes'] if Path(x['ruta']).name in ('REGLA.json','RETENCION_PRIMER_ANIO_AGREGADO.json')}
    assert len(indicators)>=2 and all(sha(p)==h for p,h in indicators.items())
    initial=load(P.parent/'h010_20261030/ESTADO_INICIAL.json')
    assert all(sha(ROOT/p)==v for p,v in initial['ajenos'].items()) and all(s in git('status','--porcelain').splitlines() for s in initial['status_ajenos'].splitlines())
    residuals=[(x['motivo'],x['n'],requirements[x['motivo']]) for x in cov['residual']]
    dump(OUT/'REQUISITOS_E.json',{m:{'contextos':n,'requisito':w} for m,n,w in residuals})
    yrrows=[]
    for x in control:
        for r in x['MU_documental']:yrrows.append([x['plan'],r['anio'],r['codigo'],r['personas']])
    report=OUT/'INFORME_H012.md'
    report.write_text(f'''# H012 · Familia IECIREOL y versiones de continuadores

**CANDIDATA.** La cobertura histórica pasa de 2.872 a {3049-ee:,} contextos respaldados sobre 3.049. El residual pasa de 177 a {ee} ({decimal(100*ee/3049,2)} %). La meta es ≤0,1 %. Las 99 posiciones conservan 99 respaldos. Las 80 altas proceden de la corrección C1 y de un único código admisible del año. D7 aporta cero asignaciones y D8 cero asignaciones autónomas.

## Familia · B/C

Tanto el nombre del programa en el listado UMAS como C1 en oferta SIES corresponden a Ingeniería en Informática. C3 corresponde a Ingeniería en Conectividad y Redes. El campo NOMPESTUD contiene el identificador del plan. La columna Nombre_L contiene el nombre de la carrera. El control por plan y por año sólo encontró C1 para los cuatro planes IECIREOL. CORRECCION_FAMILIA_H002_CANDIDATA.json conserva las filas H002 originales y el ajuste candidato. En el residual revisado ninguna otra denominación de plan presentó candidatos H002 de más de una carrera SIES. Personas distintas por celda, sin sumar entre años.

{table(['Plan','Año','Código MU documental','Personas'],yrrows)}

## Validación D7 · C

Se ocultaron todos los códigos de la persona evaluada y se exigieron al menos tres personas distintas restantes con código unánime. Unidad del control amplio: persona × plan × año × código distinto. La medida de precisión usa sólo predicciones emitidas. La regla requiere ≥99,9 % antes de redondear.

{table(['Universo','Aciertos','Errores','Abstenciones','Precisión'],[(name,v['ACIERTO'],v['ERROR'],v['ABSTENCION'],decimal(precision)+' %') for name,v,precision in [('MU documental con plan/año',val['totales'],val['precision_pct']),('Sólo DOCUMENTAL_T1',val['solo_DOCUMENTAL_T1'],val['precision_DOCUMENTAL_T1_pct']),('Contextos DOCUMENTAL_T1 con versiones idénticas en perfiles H011',val['contextos_DOCUMENTAL_T1_con_versiones_identicas_en_perfiles_H011'],val['precision_dominio_H011_pct'])]])}

El límite se incumple incluso en el control de perfiles idénticos. Se conserva la distribución de códigos del mismo plan/año, o del año posterior y después anterior cuando falta ese año, en RESIDUAL_H012.json. La validación es dentro del año. El riesgo del traslado entre años no se midió.

## Vigencia de continuadores · A/D/C

El instructivo de Oferta Académica CFT/IP 2027, página 28, y su texto en oferta_academica_2027/01_fuentes_oficiales/Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt, líneas 562–564, distinguen 1 (vigente con nuevos), 2 (sin nuevos, con antiguos) y 3 (no vigente, sin estudiantes). En los registros históricos de oferta se observaron los literales «Vigente con estudiantes nuevos» y «Vigente sin estudiantes nuevos». La decisión D8 admite ambos para el mismo expediente con T1 o matrícula anterior acreditados y sin ingreso en el año. Sólo se admiten opciones con perfil anual compatible. El año de origen, por sí solo, no acredita una matrícula anterior.

De los 28 contextos H011 sin VIGENCIA 1 compatible, 24 de IIND20251 y uno de ICIB20241 carecen de calce de perfil, y otro de ICIB20241 carece de familia/oferta anual. Los dos de TPCRE20191 acreditan matrícula previa y tienen dos versiones admisibles. D7 no se habilitó. La distribución de referencia no es unánime en ambos casos.

## Residual histórico · E

{table(['Motivo','Contextos','Requisito'],residuals)}

Se conservan los casos por plan, año, período y motivo. Las 23 referencias unánimes siguen sujetas al control metodológico global. La falta de tres personas en un año observado no habilita saltar al año siguiente.

## Reproducción

Ejecutar resolver.py y luego cerrar.py con el Python local del proyecto. FUENTES_H012.json identifica las entradas por SHA-256. La tabla histórica y el detalle por persona se procesaron en memoria. El único derivado individual está en el directorio privado de H012. R01–R04 y R19 tienen 0,00 pp de diferencia por conservación de fuentes. v20 sigue activo y v21 candidata.
'''.replace(f'{3049-ee:,}',f'{3049-ee:,}'.replace(',','.')))
    mp=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.json'
    m=load(mp);r=next(x for x in m['resultados'] if x['id']=='R30')
    r.update(resultado_clave=f'CANDIDATA H011/H012. {3049-ee} de 3.049 con respaldo y {ee} E, 99 de 99 posiciones. Familia IECIREOL candidata C1. D7 no alcanza 99,9 %. D8 sin altas autónomas. R01–R04 y R19 con 0,00 pp.',archivo=rel(report),sha256=sha(report),script_productor=rel(OUT/'resolver.py'),commit='PUBLICACION_H012; base dd34eaf',hoja_o_seccion='Familia, validación D7, vigencia y residual histórico',no_recalcular_salvo='Nueva evidencia de familia, perfil, versión o matrícula anterior, o nueva decisión explícita validada por Alexi.')
    mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    md=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.md';line='| '+' | '.join([r['id']+' · '+r['pregunta']]+[r[k] for k in ['resultado_clave','archivo','script_productor','commit','sha256','clase','fecha_resultado','no_recalcular_salvo']])+' |'
    md.write_text('\n'.join(line if x.startswith('| R30 ·') else x for x in md.read_text().splitlines())+'\n')
    paths=sorted({rel(q) for q in OUT.iterdir() if q.is_file()}|{rel(mp),rel(md),rel(OUT/'QA_H012.json'),rel(OUT/'LISTA_PUBLICACION.json')})
    dump(OUT/'LISTA_PUBLICACION.json',{'rutas':paths,'base':'dd34eaf','estado':'CANDIDATA'})
    dump(OUT/'QA_H012.json',{'estado':'PASS_CON_D7_NO_HABILITADA','pruebas':5,'reproduccion':{q.name:h for q,h in checks.items()},'v20_intacto':True,'asignaciones_previas_intactas':True,'99_posiciones_intactas':True,'tasas_delta_pp':0.0,'fuentes_indicadores':indicators,'25_ajenos_intactos':True,'meta_residual_alcanzada':100*ee/3049<=0.1,'hallazgos_privacidad':[]})
    db=sqlite3.connect(Path(d['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
    ids={str(v) for row in db.execute('select persona,codcli from observaciones') for v in row if v is not None};db.close();ids.update({v.split('-')[0] for v in ids if '-' in v})
    pattern=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(x) for x in sorted(ids) if len(x)>=6)+r')(?!\w)')
    generic=re.compile(r'(?<!\w)(?:\d{7,8}-[0-9Kk]|\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]|\+56\s*[29]\s*\d{4}\s*\d{4}|[29]\d{8})(?!\w)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
    for path in paths:
        assert Path(path).suffix in ('.md','.json','.py')
        for line in (ROOT/path).read_text().splitlines():assert not pattern.search(line) and not generic.search(line),path
    print('PASS',len(paths),'archivos;',ee,'E')
if __name__=='__main__':main()
