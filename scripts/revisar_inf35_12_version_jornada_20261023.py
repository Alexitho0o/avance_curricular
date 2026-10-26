"""Revisión acotada INF35-12. Solo lectura de fuentes y diccionario vigente."""
from pathlib import Path
import sys, json, collections, datetime, subprocess
from zoneinfo import ZoneInfo
import openpyxl

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, sha256
from common.catalogos_sies import cargar_catalogo, resolver_catalogo

now = datetime.datetime.now(ZoneInfo('America/Santiago'))
stamp = now.strftime('%Y%m%d_%H%M%S')
O = R / 'outputs' / ('revision_inf35_12_version_jornada_' + stamp)
P = Path.home() / '.local/share/ipss' / O.name
assert subprocess.run(['git', '-C', str(P.parent), 'rev-parse', '--show-toplevel'], capture_output=True).returncode != 0
O.mkdir(); P.mkdir(mode=0o700)
H = {}
def record(p, expected=None):
    p = Path(p); h = sha256(p)
    if expected: assert h == expected, str(p)
    H[str(p)] = h
    return p
def read(p, expected=None):
    return json.loads(record(p, expected).read_text())
def dump(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2, default=str) + '\n')
    if p.is_relative_to(P): p.chmod(0o600)
def norm(v):
    if v is None: return ''
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v).strip()

git = lambda *a: subprocess.check_output(['git', '-C', str(R), *a], text=True).strip()
before_git = {'rama': git('branch', '--show-current'), 'HEAD': git('rev-parse', 'HEAD')}
active = read(R / 'data/diccionario_sies_seguimiento/activo.json')
desc = read(R / active['descriptor'], active['sha256'])
record(desc['base_privada']['ruta'], desc['base_privada']['sha256'])
assert desc['edicion'] == 'v3_20261023_inf35_07'
old = R / 'outputs/cierre_inf35_07_jornadas_14_20261023_135630'
manifest = read(old / 'MANIFEST.json')
priv = Path(manifest['privado'])
targets = read(priv / 'JORNADAS_14_PENDIENTES.json', manifest['privados_hashes']['JORNADAS_14_PENDIENTES.json'])
targets = [x for x in targets if x['caso'] == 'INF35-12']
assert len(targets) == 2
t = targets[0]
cuts = read(priv / 'FILAS_CORTES_VERIFICADAS.json', manifest['privados_hashes']['FILAS_CORTES_VERIFICADAS.json'])
cuts = [x for x in cuts if x['caso'] == 'INF35-12']
prior = R / 'outputs/revision_35_informatica_20261023_130829'
pm = read(prior / 'MANIFEST.json')
rows = read(Path(pm['privado']) / 'FILAS_RELEIDAS.json', pm['privado_hashes']['FILAS_RELEIDAS.json'])
rows = [x for x in rows if x.get('caso') == 'INF35-12']
assert len(cuts) == 6 and len(rows) == 16

# Releer las filas primarias, no dar por buena solamente la extracción anterior.
groups = collections.defaultdict(list)
for x in rows + cuts:
    record(x['fuente'], x['sha256']); groups[(x['fuente'], x['hoja'])].append(x)
checked = 0
for (path, sheet), expected in groups.items():
    w = openpyxl.load_workbook(path, read_only=True, data_only=True)
    it = iter(w[sheet].values)
    for header_row, values in enumerate(it, 1):
        headers = [norm(v).upper() for v in values]
        if 'CODCLI' in headers or 'ANIO_INFORMADO' in headers: break
        if header_row >= 5: raise ValueError('Encabezado no encontrado: '+Path(path).name)
    assert 'CODCLI' in headers or 'ANIO_INFORMADO' in headers
    wanted = {x['fila']: x for x in expected}
    for n, values in enumerate(it, header_row+1):
        if n > max(wanted): break
        if n not in wanted: continue
        actual = dict(zip(headers, values)); x = wanted[n]
        for k in ['CODCLI','JORNADA','CODCARPR','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO','SITUACION','REGIMEN','N_DOC','DV','TIPO_DOC','ANIO_INFORMADO','COD_SED','COD_CAR','JOR','VERSION','ANIO_ING_ORI','ANIO_ING_ACT','VIG']:
            if k in x: assert norm(actual[k]) == norm(x[k]), (Path(path).name, n, k)
        if 'RUT' in x: assert norm(actual['RUT']) == norm(x['RUT'])
        checked += 1
    w.close()
    print(Path(path).name, sheet, 'verificado', flush=True)
assert checked == 22

s = DiccionarioSiesSeguimiento()
observations = [json.loads(v) for (v,) in s.db.execute('select payload from observaciones where persona=? and codcli=?', (t['persona'], t['CODCLI']))]
assert {x['observacion_id'] for x in observations} == {24594,24595,24596}
assert all(x['plan'] == 'IINF20241' and str(x['ano']) == '2026' for x in observations)
mu = s.codigos_mu(persona=t['persona'], anio=2026)
assert mu['codigos'] == ['I162S2C1J4V2']
assert next(x for x in observations if x['periodo']=='1')['codigo_interno_adoptado'] == 'I162S2C1J4V2'
assert all(not x['codigo_interno_adoptado'] for x in observations if x['periodo'] in ['2','3'])
peers = [json.loads(v) for (v,) in s.db.execute("select payload from observaciones where plan='IINF20241' and anio='2026' and periodo='1' and jornada='1'")]
documented = [x for x in peers if x['codigo_documental_atribuible']]
assert len(peers)==32 and len(documented)==28
assert len({x['persona'] for x in documented})==28
assert {x['codigo_documental_atribuible'] for x in documented} == {'I162S2C1J1V2'}
new = [x for x in documented if str(x['fechas_declaradas']['DA_ANOINGRESO'])=='2026']
assert len(new)==12
# Literal MU cotejado para los 28 comparadores; no es regla por mayoría.
for x in documented:
    assert 'I162S2C1J1V2' in s.codigos_mu(persona=x['persona'],anio=2026)['codigos']

catpath = record(R/'data/catalogos_sies/2026/mu2026_20261013/catalogo.json')
cat = cargar_catalogo(2026)
resolved = {j: resolver_catalogo(cat, codcarpr='IINF', sede='RE', jornada=j) for j in ['O','D']}
assert resolved['O']['codigo_unico']=='I162S2C1J4V2'
assert set(resolved['D']['candidatos'])=={'I162S2C1J1V1','I162S2C1J1V2'}
hp = R/'data/versiones_historicas_sies_umas/fase_b_20261015/perfiles_sies_anuales.json'
hm = read(hp.parent/'manifest.json')
profiles = read(hp, hm['salidas'][hp.name])
codes = {'I162S2C1J1V1','I162S2C1J1V2','I162S2C1J4V2'}
offer = [x for x in profiles if x['anio']==2026 and x['codigo_unico'] in codes]
assert len(offer)==3
offer_summary = [{ 'codigo':x['codigo_unico'], 'registro_csv':x['registro_csv'], **{k:x['campos_originales'][k] for k in ['Vigencia','Duración Estudios','Tipo Carrera','Año Inicio']}} for x in offer]
assert next(x for x in offer_summary if x['codigo']=='I162S2C1J1V1')['Vigencia']=='Vigente sin estudiantes nuevos'
before = next(x for x in cuts if x['corte_nominal'].startswith('2026-09-29'))
after = next(x for x in cuts if x['corte_nominal'].startswith('2026-09-30'))
assert before['JORNADA']=='O' and after['JORNADA']=='D'
assert before['FECHAMATRICULA']==after['FECHAMATRICULA']
prom = [x for x in rows if 'PLAN_DE_ESTUDIO' in x]
assert {x['PLAN_DE_ESTUDIO'] for x in prom}=={'IINF20241'}
assert {x['REGIMEN'] for x in prom}=={'TRIMESTRAL'}
oldprom = [x for x in prom if '7804' in x['fuente']]
newprom = [x for x in prom if '12166' in x['fuente']]
assert len(oldprom)==5 and len(newprom)==5
overlap = [(a,b) for a in oldprom for b in newprom if all(a[k]==b[k] for k in ['CODCLI','PLAN_DE_ESTUDIO','ANO','PERIODO','CODRAMO'])]
assert len(overlap)==2 and all(a['JORNADA']=='O' and b['JORNADA']=='D' for a,b in overlap)
dump(P/'EVIDENCIA_PRIVADA.json', {'objetivo':targets,'observaciones':observations,'mu':mu,'fotos':cuts,'filas_primarias':rows,'comparadores_documentados':documented,'coincidencias_jornada_actual':overlap})
dump(O/'CATALOGO_Y_OFERTA.json', {'resolucion_operativa':resolved,'oferta_historica_2026':offer_summary})
result = {
 'caso':'INF35-12','anio':2026,'plan':'IINF20241','clasificacion':'B observado; C contraste; E propuestas sin adoptar',
 'codigo_T1_documentado':'I162S2C1J4V2',
 'ultimo_corte_O':before['corte_nominal'],'primer_corte_D':after['corte_nominal'],
 'comparadores':{'contextos':32,'personas_documentadas_J1V2':28,'con_ingreso_DA_2026':12,'contextos_sin_atribucion_documental':4},
 'destinos':[
  {'periodo':2,'codigo_propuesto':'I162S2C1J4V2','estado':'REUTILIZABLE_EN_FOTOS_O; PROPUESTA_NO_ADOPTADA_PARA_PERIODO_COMPLETO','evidencia':'T1 literal + O en respaldo congelado julio, agosto y 29-septiembre. Plan IINF20241.','pendiente':'Las fotos delimitan el cambio observado; no prueban que toda actividad nativa período 2 ocurriera en O ni fecha administrativa efectiva.'},
  {'periodo':3,'codigo_propuesto':'I162S2C1J1V2','estado':'CORRESPONDENCIA_INTERNA_PROPUESTA_NO_ADOPTADA','evidencia':'D desde foto 30-septiembre y 2-octubre; plan IINF20241; dos asignaturas período 3; oferta V2 para nuevos y 28 comparadores documentados.','pendiente':'Catálogo operativo mantiene V1/V2; falta equivalencia individual destino. La unanimidad del grupo y vigencia para nuevos corroboran, pero no prueban versión de traslado. Atribución documental pendiente.'}],
 'cierres_aplicados':0,'tasas_y_denominadores_modificados':False,
 'limites':['No se equipara jornada vigente en exportación con jornada histórica de cada asignatura.','No se usa igualdad de número V entre jornadas como regla.','No se declara fecha exacta de cambio ni aceptación individual por SIES.']}
dump(O/'RESULTADO.json', result)
for f,h in H.items(): assert sha256(f)==h
after_git={'rama':git('branch','--show-current'),'HEAD':git('rev-parse','HEAD')}
assert after_git==before_git
assert [json.loads(v) for (v,) in s.db.execute('select payload from observaciones where persona=? and codcli=?',(t['persona'],t['CODCLI']))]==observations
s.close()
dump(O/'QA.json', {'resultado':'OK_REVISION; ADJUDICACION_PENDIENTE','filas_primarias_releidas':checked,'comparadores_documentados':28,'identidad_expediente_plan_verificados':True,'jornada_actual_no_retropropagada':True,'fuentes_diccionario_inalterados':True,'denominadores_inalterados':True,'git_antes':before_git,'git_despues':after_git,'commit_push':False})
(O/'INFORME.md').write_text('''# INF35-12 · versión SIES antes/después del cambio de jornada

**B/C.** Año 2026, expediente IINF, plan IINF20241. La MU T1 documenta
`I162S2C1J4V2`. El diccionario vigente ya conserva ese código como ancla T1.

| Momento | Código respaldado o propuesto | Resultado |
|---|---|---|
| T1 y fotos anteriores al cambio O→D | I162S2C1J4V2 | B código MU literal; C reutilización en la jornada O observada |
| T2-2026 | I162S2C1J4V2 | C propuesta de continuidad del ancla; E alcance del período completo pendiente |
| Después del cambio D / T3-2026 | I162S2C1J1V2 | C/E propuesta de correspondencia interna, no atribución documental |

**B.** Se mantiene O en el respaldo congelado en julio y en las fotos del
25-agosto y 29-septiembre. La foto del 30-septiembre cambia a D y situación
49; el 2-octubre sigue D. El intervalo observado es 29-09-2026 12:00:39 →
30-09-2026 12:00:38. Zona horaria de las fotos no confirmada. FECHAMATRICULA
no cambia y no es la fecha de este evento. No se ha acreditado el día efectivo.

**B.** PROMEDIOS7804 y PROMEDIOS12166 conservan IINF20241. Dos homologaciones
del mismo período 1 cambian de jornada O a D entre exportaciones: la jornada
actual no acredita la jornada histórica de la asignatura. El régimen registrado
es TRIMESTRAL; período 2 tiene una aprobación y período 3 dos filas sin
calificación concluyente. Estas filas no se convierten en una tasa de retención.

**B/C.** El catálogo operativo 2026 resuelve IINF/RE/O como J4V2, pero
IINF/RE/D entrega J1V1 y J1V2. Ambas son regulares, de ocho semestres.
La oferta histórica 2026 describe J1V1 como vigente sin estudiantes nuevos y
J1V2 como vigente con estudiantes nuevos. El plan IINF20241, por sí solo, no
elimina la ambigüedad: existen antecedentes de ese plan con V1 en otros años.

**B/C.** En el diccionario común, los 32 contextos T1-2026 del mismo plan y
jornada D incluyen 28 personas con atribución documental J1V2 y cuatro sin
atribución. Doce de las 28 tienen ingreso DA 2026. El código se contrastó con
el índice MU de cada persona. Es corroboración, no una regla por mayoría ni
una prueba individual para INF35-12.

**E.** J1V2 es la propuesta de destino respaldada por estos elementos; la
oferta para nuevos no demuestra por sí sola la versión de un cambio de
jornada. No corresponde cerrar documentalmente T3 ni trasladar D hacia T2.
Para adoptar estos destinos hace falta una decisión interna explícita y acotada
que acepte las fotos como referencia del corte y J1V2 como equivalencia de
destino, manteniendo pendiente la atribución documental. No falta localizar
la identidad; falta ese respaldo o decisión de atribución.

**C.** Se releyeron 22 filas primarias; se conservaron originales, diccionario
activo v3, bases, Excel y denominadores. Sin commit/push. RESULTADO.json y
CATALOGO_Y_OFERTA.json contienen resultados; MANIFEST.json fija hashes y
la ruta privada con fuentes/hojas/filas e identidades. QA.json explicita límites.
''')
(O/'CHECKPOINT.md').write_text('B/C: revisión INF35-12 terminada. Dicc. v3 sin cambios. C/E: T2 J4V2 y T3 J1V2 propuestas acotadas, no adoptadas. Pendiente decisión interna; atribución documental sigue abierta. No reconstruir el cruce de identidad ni volver a usar jornada actual como histórica. Consultar RESULTADO.json y evidencia privada antes de continuar.\n')
dump(O/'MANIFEST.json', {'fecha_hora':now.isoformat(),'proceso':'Seguimiento interno intertrimestral IPSS 162','caso':'INF35-12','anio_datos':2026,'clasificacion':'B/C revisión; E adjudicación pendiente','fuentes_sha256':H,'privado':str(P),'privado_hashes':{p.name:sha256(p) for p in P.iterdir()},'salidas_sha256':{p.name:sha256(p) for p in O.iterdir()},'script':str(Path(__file__)),'script_sha256':sha256(Path(__file__)),'especificacion':str(R/'docs/ESPECIFICACION_REVISION_INF35_12_20261023.md'),'especificacion_sha256':sha256(R/'docs/ESPECIFICACION_REVISION_INF35_12_20261023.md'),'git':after_git,'sin_commit_push':True,'nuevas_adjudicaciones':0})
print(json.dumps({'salida':str(O),'manifest_sha256':sha256(O/'MANIFEST.json'),'QA':'OK revisión; adjudicación pendiente'},ensure_ascii=False))
