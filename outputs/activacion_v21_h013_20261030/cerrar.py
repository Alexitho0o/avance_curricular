"""Documenta la activación verificada. Sólo publica agregados y metadatos."""
from pathlib import Path
import json,re,sqlite3,subprocess
from construir_v21 import ROOT,D,P,OUT,OLD,load,dump,sha
def table(h,rows):
    return '\n'.join(['| '+' | '.join(h)+' |','|'+'---|'*len(h)]+['| '+' | '.join(str(v) for v in row)+' |' for row in rows])
def money(v):return f'{v:.2f}'.replace('.',',')
def rel(p):return str(p.relative_to(ROOT))
def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
def main():
    qa=load(OUT/'QA_ACTIVACION.json');assert qa['estado']=='PASS'
    active=load(ROOT/'data/diccionario_sies_seguimiento/activo.json')
    assert active['sha256']==sha(D/'descriptor.json') and active['descriptor']==rel(D/'descriptor.json')
    cob=load(OUT/'COBERTURA.json');error=load(OUT/'ERROR_D7.json');assert len(error)==1
    detail=load(OUT/'DESCALCES_41.json');total=sum(sum(x['resultados'].values()) for x in detail);assert total==41
    rows=[]
    for x in detail:
        p=x['perfil'];key=x['clave']
        candidates=', '.join(f"{c} ({v['total']} sem., {v['tipo']}, {v['modalidad']})" for c,v in p['opciones'].items())
        mu=' / '.join(str(y)+' '+', '.join(c+' × '+str(n) for c,n in dist.items()) for y,dist in x['mu_documental_por_anio'].items())
        cause='La oferta 2025 no contiene V2. En 2026 se documentan 83 personas en V2.' if key[1]=='IIND20251' else 'Ocho semestres derivados frente a opciones de cuatro o cinco. El catálogo de 2020 y la referencia posterior difieren.' if key[1] in ('IECSREOL20211','ICIB20241') else 'La comparación H011 exigía modalidad no presencial en la derivación. Aquí hay versiones presenciales, incluso con duración coincidente.'
        rows.append([key[1],key[-1],p['nivel_maximo'],p['regimen'],str(p['semestres_exactos'])+' → '+str(p['semestres_convertidos']),candidates,mu,str(x['resultados']),cause])
    (OUT/'DESCALCES_41.md').write_text('# Contraste por plan y año · 41 contextos\n\nB/C corresponde al contraste de fuentes. D corresponde a la extensión aprobada. Los códigos asignados se rotulan VERSION_POR_MU_DEL_PLAN y la duración derivada queda «conversión no confirmada» para ese plan. Las causas son hipótesis E. Las fuentes disponibles no permiten atribuir el descalce a niveles incompletos. Se conservan régimen, nivel y catálogo originales.\n\n'+table(['Plan','Año','NIVEL','Régimen','Exacto → semestres','Oferta anual','MU documental por año (personas por código)','Resultado','Lectura probable C/E'],rows)+'\n')
    reasons={
    'CODIGO_MU_PLAN_AUSENTE_OFERTA_ANUAL':'Acreditar oferta aceptada del año del contexto y versión efectivamente informada. Para IIND20251 confirmar V2 en 2025 o documentar su ausencia.',
    'MU_PLAN_MENOS_DE_TRES_PERSONAS':'Aportar T1 documental atribuible al expediente y plan, o referencia unánime suficiente del año aplicable.',
    'MU_PLAN_NO_UNANIME':'Distinguir versiones por expediente y plan con evidencia anual individual en carpeta restringida.',
    'PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO':'Calendario UMAS y definición de los períodos 4/5 por año y régimen semestral/trimestral.',
    'PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS':'Primera matrícula del expediente/plan con fecha, sede y jornada efectiva del cambio.',
    'SIN_CODIGO_ANUAL_COMPATIBLE':'Equivalencia formal de plan y versión del año con sede, jornada y duración.',
    'SIN_FAMILIA_H002_U_OFERTA_ANUAL':'Acreditar familia o existencia del código en la oferta del año.',
    'T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO':'Documento que concilie el código del T1 con la oferta y el perfil del año del contexto.'}
    erows=[(z['motivo'],z['n'],reasons[z['motivo']]) for z in cob['residual']]
    (OUT/'SOLICITUD_UMAS_RESIDUAL.md').write_text('# Solicitud a UMAS · borrador pendiente de envío\n\nPara cerrar los 59 contextos pendientes del seguimiento, solicitamos los siguientes respaldos por plan, sede, jornada y año. RESIDUAL.json detalla las combinaciones y sus conteos. Enviar primero el catálogo y calendario sin nóminas. Si es indispensable verificar una matrícula, depositar el extracto mínimo en la carpeta restringida, con año, expediente, plan, sede, jornada y código informado. Indicar fuente, fecha y responsable de extracción.\n\n'+table(['Grupo de evidencia','Contextos','Respaldo solicitado'],erows)+'\n')
    levels=sorted({x['nivel_asignacion'] for k in ('historico','posiciones99') for x in cob[k]})
    levels_table=[(v,*[next((r['n'] for r in cob[k] if r['nivel_asignacion']==v),0) for k in ('historico','posiciones99')]) for v in levels]
    vals=qa['puntero_real_v21']['tasas'];rrows=[(k,v['numerador'],v['denominador'],money(v['tasa_pct']),money(v['delta_pp'])) for k,v in vals.items()]
    arch=ROOT/'data/diccionario_sies_seguimiento/archivo_v20_h013'
    (arch/'ARCHIVO_V20.md').write_text(f'# v20 archivada · decisión de Alexi, 30-10-2026\n\nLa edición activa a 27-10 quedó archivada al activar H013. La carpeta conserva el puntero original, con SHA-256 `{sha(arch/"activo.json")}`. Descriptor original `{OLD}`, SHA-256 `{sha(ROOT/OLD)}`. Base privada original SHA-256 `{load(ROOT/OLD)["base_privada"]["sha256"]}`. H002 reproduce su evidencia congelada con este puntero y verifica el mismo hash en lectura y cierre.\n')
    report=OUT/'INFORME_H013.md'
    report.write_text(f'''# H013 · v21 activa

D · Alexi, 30-10-2026. Se acepta el riesgo de D7 con 956 aciertos, 1 error y 233 abstenciones (99,8955 % sobre 957 predicciones). El caso fue IECIREOL20201 en 2021. Se predijo V1 y la MU informó V2 en la misma familia C1J4. Al conservar todos los documentales se observan diez personas en V1 y una en V2. Cuando se ocultó esa persona, las diez referencias restantes eran unánimes. La correspondencia interna conserva su nivel y no acredita documentalmente al contexto.

La referencia de D7 prioriza mismo plan y año. En ausencia de documentales busca primero el T1 posterior y luego el anterior. Un año con evidencia mixta o insuficiente queda E. Se exigen tres personas distintas y presencia del código en la oferta del año. Las 23 altas esperadas se verificaron (13 TTMREOL20211 y 10 IETMREOL20211, año 2021). La extensión resuelve 15 de 41 descalces. DESCALCES_41.md contiene oferta, niveles, duración derivada, referencia MU y lectura por plan/año. IIND20251 conserva 24 E.

## Cobertura final

2.990 de 3.049 contextos respaldados y 59 E (1,94 %). Las 99 posiciones conservan sus 99 respaldos. A continuación se cuentan contextos o posiciones, sin sumar entre columnas.

{table(['Nivel','3.049 contextos','99 posiciones'],levels_table)}

## Recálculo institucional

{table(['Indicador','Numerador','Denominador','Tasa %','Diferencia pp'],rrows)}

QA_ACTIVACION.json conserva los controles con el puntero v20, con el puntero v21 aislado y con el puntero v21 real. H001 se recalculó sobre su MU congelada y el catálogo de carreras. R19 se recalculó con los indicadores de la foto V24 aprobada. Se reagruparon numeradores y denominadores por los códigos de cada puntero, conservando los casos sin contexto y múltiples. El ingreso T2 usa matrículas menos renuncias sobre el total por área. Su fuente no contiene clave individual para asociar código de contexto. R19 conserva el estado BORRADOR.

## Activación y contrato

Descriptor activo `{active['descriptor']}`, SHA-256 `{active['sha256']}`. El puntero v20 archivado conserva todos sus hashes. La base nueva incluye las tablas MU y una copia íntegra de cada fila de observaciones v20 en observaciones_archivo_v20. La proyección observaciones entrega el código documental únicamente para DOCUMENTAL_T1 y el código interno para adjudicaciones D. La tabla asignaciones_v21 contiene nivel, regla, año fuente, evidencia, clase y código. El consumidor devuelve esos campos en evidencia. El año de referencia de D7 es del plan, sin implicar T1 propio de la persona. La capa PROMEDIOS conserva sus bytes privados y sus claves de observación, con metadatos vinculados al SHA-256 de v21.

Las tres interfaces de consulta se probaron con 78 contextos por interfaz, seis por nivel, y con capa PROMEDIOS disponible. MU2027 evaluó 4.105 filas de antiguos. H001 y R19 usan sus bases aprobadas para la población y el resultado. H002 consulta un catálogo histórico fijado a v20. En el primer ensayo, la comprobación del hash del puntero histórico detectó el cambio y se restauró v20. La lectura de H002 se dirigió a la copia archivada, con el mismo hash exigido por FUENTES.json. Pasaron 11 pruebas de paridad y 27 de MU2027.

## Residual

{table(['Motivo','Contextos','Requisito'],erows)}

SOLICITUD_UMAS_RESIDUAL.md es un borrador. La reproducción aislada produjo la misma base SQLite y las mismas asignaciones privadas. Antes de publicar se escanearon únicamente archivos agregados y de código. Ningún libro ni detalle individual forma parte de este respaldo.
''')
    mp=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.json';m=load(mp)
    r=next(r for r in m['resultados'] if r['id']=='R29');r.update(resultado_clave='ACTIVA v21 H013. 2.990 de 3.049 contextos y 99 de 99 posiciones respaldadas. Quedan 59 E. Recálculo R01–R04 y R19 con 0,00 pp.',archivo=rel(report),sha256=sha(report),script_productor=rel(OUT/'activar.py'),commit='PUBLICACION_H013; base 989198f',hoja_o_seccion='Cobertura, activación y recálculo',clase='D activación; B/C evidencia y recálculo; E residual',limites='VERSION_POR_MU_DEL_PLAN es correspondencia interna. Riesgo D7 aceptado. 59 contextos requieren evidencia adicional.',no_recalcular_salvo='Nueva evidencia de las combinaciones de RESIDUAL.json o control explícito de Alexi.')
    arc={'id':'R31','pregunta':'¿Qué edición respalda las reproducciones históricas que fijaron v20?','resultado_clave':'ARCHIVADA v20. Descriptor y base privada íntegros. H002 verifica el puntero histórico por su hash original.','archivo':rel(arch/'ARCHIVO_V20.md'),'hoja_o_seccion':'Archivo de v20','script_productor':rel(OUT/'construir_v21.py'),'commit':'PUBLICACION_H013; base 989198f','sha256':sha(arch/'ARCHIVO_V20.md'),'clase':'B hash; D archivo','fecha_resultado':'2026-10-30','no_recalcular_salvo':'Verificación expresa de la instantánea histórica.','limites':'La selección operativa se resuelve por activo.json.'}
    m['resultados']=[x for x in m['resultados'] if x['id']!='R31']+[arc];mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    def line(z):
        return '| '+' | '.join([z['id']+' · '+z['pregunta']]+[z[k] for k in ['resultado_clave','archivo','script_productor','commit','sha256','clase','fecha_resultado','no_recalcular_salvo']])+' |'
    md=ROOT/'docs/MAPA_RESULTADOS_GOBERNADOS.md';s=md.read_text().replace('## Mapa (30 resultados)','## Mapa (31 resultados)')
    s='\n'.join(line(r) if l.startswith('| R29 ·') else l for l in s.splitlines() if not l.startswith('| R31 ·'))+'\n';md.write_text(s.replace('\n## Límites por resultado','\n'+line(arc)+'\n\n## Límites por resultado'))
    paths={rel(f) for f in [*OUT.iterdir(),*D.iterdir(),*arch.iterdir()] if f.is_file()}
    paths.update([rel(md),rel(mp),'data/diccionario_sies_seguimiento/activo.json','outputs/paridad_codigo_sies_20261029/construir_paridad.py',rel(OUT/'QA_FINAL.json'),rel(OUT/'LISTA_PUBLICACION.json')])
    dump(OUT/'LISTA_PUBLICACION.json',{'rutas':sorted(paths),'base':'989198f'})
    checks=load(P.parent/'h010_20261030/ESTADO_INICIAL.json')
    assert all(sha(ROOT/f)==h for f,h in checks['ajenos'].items()) and all(s in git('status','--porcelain').splitlines() for s in checks['status_ajenos'].splitlines())
    assert sha(load(ROOT/OLD)['base_privada']['ruta'])==load(ROOT/OLD)['base_privada']['sha256']
    db=sqlite3.connect(Path(load(ROOT/OLD)['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
    ids={str(v) for row in db.execute('select persona,codcli from observaciones') for v in row if v is not None};db.close();ids.update({v.split('-')[0] for v in ids if '-' in v})
    pat=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(x) for x in sorted(ids) if len(x)>=6)+r')(?!\w)')
    generic=re.compile(r'(?<!\w)(?:\d{7,8}-[0-9Kk]|\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]|\+56\s*[29]\s*\d{4}\s*\d{4}|[29]\d{8})(?!\w)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
    dump(OUT/'QA_FINAL.json',{'estado':'PASS_ACTIVA_V21','puntero_real':active,'control_numeradores_denominadores':True,'reproduccion_privada':{'base':sha(P/'DICCIONARIO_V21.sqlite'),'asignaciones':sha(P/'ASIGNACIONES_H013_PRIVADAS.json')},'descalces':41,'38_altas':True,'v20_archivada_intacta':True,'25_ajenos_intactos':True,'hallazgos_privacidad':[]})
    for f in paths:
        assert Path(f).suffix in ('.json','.md','.py')
        for l in (ROOT/f).read_text().splitlines():
            if pat.search(l) or generic.search(l):raise ValueError('Coincidencia de privacidad en '+f)
    print('PASS',len(paths),'rutas agregadas y de código. ')
if __name__=='__main__':main()
