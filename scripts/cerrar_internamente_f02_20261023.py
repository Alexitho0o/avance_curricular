"""Adjudicación interna autorizada, no destructiva; revisión temporal IINF20241."""
import copy
import datetime as dt
import hashlib
import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

import openpyxl

R = Path(__file__).resolve().parents[1]
P = Path.home() / '.local/share/ipss'
now = dt.datetime.now(ZoneInfo('America/Santiago'))
stamp = now.strftime('%Y%m%d_%H%M%S')
O = R / 'outputs' / ('cierre_interno_f02_' + stamp)
Q = P / ('cierre_interno_f02_' + stamp)
assert subprocess.run(['git', '-C', str(P), 'rev-parse', '--show-toplevel'], capture_output=True).returncode != 0
os.umask(0o077)
O.mkdir()
Q.mkdir(mode=0o700)
hashes = {}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def source(p, expected=None):
    p = Path(p)
    h = sha(p)
    assert expected is None or h == expected, 'Hash incompatible: ' + str(p)
    hashes[str(p)] = h
    return p

def load(p, expected=None):
    return json.loads(source(p, expected).read_text())

def dump(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str) + '\n')

def git():
    return {k: subprocess.check_output(['git', '-C', str(R), *args], text=True).strip()
            for k, args in [('rama', ['branch','--show-current']), ('head', ['rev-parse','HEAD']),
                            ('remotos', ['remote','-v']), ('status', ['status','--short'])]}

before_git = git()
dump(O / 'GIT_ANTES.json', before_git)
bm = load(R / 'outputs/reproduccion_puente_20261023_004044/MANIFEST.json')
bp = Path(bm['privado'])
obs = load(bp / 'OBSERVACIONES_PRIVADAS.json', bm['salidas_privadas_hashes']['OBSERVACIONES_PRIVADAS.json'])
cases = load(P / 'cambios_plan_12_y_4_20261023_080207/REVISION_16_CASOS_FINAL.json')
case = next(x for x in cases if x['caso'] == 'F02')
person = case['persona']
review = load(P / 'trayectorias_374_20261023_072401/OBSERVACIONES_REVISADAS.json')
f = [x for x in obs if x['persona'] == person]
pending = [x for x in f if not x['codigo_interno_adoptado']]
assert len(f) == 9 and len(pending) == 4
target = next(x for x in pending if (x['plan'], x['ano'], x['periodo']) == ('IECIREOL20211','2024','2'))
rr = next(x for x in review if x['observacion_id'] == target['observacion_id'])
code = 'I162S2C1J4V2'
assert rr['candidatos_por_fecha_exclusiva'] == [code]
assert rr['codigos_anuales'] == [code]
assert any(x['expedientes_con_misma_fecha'] == 1 and x['codigo'] == code for x in rr['coincidencias_fecha'])
new_plan = [x for x in pending if x['plan'] == 'IINF20241']
assert sorted(x['periodo'] for x in new_plan) == ['1','2','3']
assert all(x['ano'] == '2024' and x['carrera'] == 'IINF' and x['jornada_sies'] == '4' for x in new_plan)

master = load(R / 'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
groups = load(R / 'data/versiones_por_cohorte/20261016/grupos_existentes.json')
manual = load(R / 'data/diccionario_sies_umas/20261015/evidencia/caracterizacion_reglas_y_fuentes.json')['equivalencias_manual_fcu2026']['filas']
offers = [x for x in master['oferta_anual'] if x['anio'] == 2024 and x['codigo_unico'].rsplit('V',1)[0] == case['familia']]
equiv = [x for x in master['candidatos_plan_sies'] if x['plan_umas'] == 'IINF20241' and x['jornada_umas'] == 'O' and x['sede_umas'] == 'RE']
manual_iinf = [x for x in manual if x.get('CODCARPR') == 'IINF']
cohort = [x for x in obs if (x['carrera'],x['plan'],x['jornada_sies'],x['ano']) == ('IINF','IINF20241','4','2024')]
counts = Counter(x['codigo_documental_atribuible'] or 'PENDIENTE' for x in cohort)
assert counts == {'PENDIENTE':70, code:330, 'I162S2C1J4V3':3}
assert not manual_iinf
assert all(not x['habilitada_para_resolver'] and x['ambito_candidato'] == 2026 for x in equiv)

# Relectura dirigida: código e identidad MU para F02 y el contraejemplo V3.
contrast = [x for x in cohort if x['codigo_documental_atribuible'] == 'I162S2C1J4V3']
checks = {}
for x in [target, *contrast]:
    for e in x['evidencias_matricula']:
        checks[e['fuente'],e['hoja'],e['fila']] = (x['persona'],e['codigo'])
for path, sheet in sorted({(p,s) for p,s,n in checks}):
    source(path, bm['fuentes_hashes'].get(path))
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    it = iter(wb[sheet].values)
    headers = next(it)
    for rowno, row in enumerate(it,2):
        key = (path,sheet,rowno)
        if key not in checks:
            continue
        d = dict(zip(headers,row))
        normalized = str(int(d['N_DOC'])) + '-' + str(d['DV']).strip().upper()
        observed = 'I162S%sC%sJ%sV%s' % tuple(str(int(d[k])) for k in ['COD_SED','COD_CAR','JOR','VERSION'])
        assert (normalized, observed) == checks[key]
        assert int(d['ANIO_INFORMADO']) == 2024
        checks[key] = True
    wb.close()
assert all(v is True for v in checks.values())

# Mantener evidencia de la fuente primaria y de los respaldos de planes.
for x in case['mu_primaria']:
    source(x['archivo'], x['sha256'])
t3manifest = load(R / 'outputs/revision_t3_2024_f02_20261023_082535/MANIFEST.json')
source(R / 'outputs/revision_t3_2024_f02_20261023_082535/INFORME_F02_T3_2024.md')
source(P / 'revision_t3_2024_f02_20261023_082535/F02_T3_DETALLE.csv')
source(P / 'revision_t3_2024_f02_20261023_082535/F02_PLAN_ANTERIOR_2024_2.json')
source(Path(__file__))
source(R / 'docs/ESPECIFICACION_CIERRE_INTERNO_F02_20261023.md')

decision = {
    'regla_id':'F02_INTERNO_2024_BIMESTRE2_V2_20261023', 'clasificacion':'D decisión; B evidencia; C aplicación',
    'responsable_decision':'Alexi, autorización explícita en este chat', 'ejecutor':'Codex',
    'fecha_hora':now.isoformat(), 'autorizacion':'Procede con el cierre interno de esa observación como V2',
    'alcance':'Una observación F02 IECIREOL20211, 2024/2 bimestral; no equivalencia universal',
    'codigo_interno_adoptado':code, 'fecha_administrativa_cambio':'Pendiente; no requerida para este cierre interno',
    'documental_sin_cambios':True, 'consumo':'Capa de adjudicación local sobre el diagnóstico; no motor anual ni bases',
    'reversion':'Omitir exclusivamente esta adjudicación; se conserva el estado anterior en el detalle privado',
}
overlay = {**decision, 'observacion_id':target['observacion_id'], 'persona':person,'CODCLI':target['CODCLI'],
           'estado_antes':copy.deepcopy(target), 'evidencias_fecha_exclusiva':rr['coincidencias_fecha']}
updated = copy.deepcopy(obs)
u = next(x for x in updated if x['observacion_id'] == target['observacion_id'])
u.update(codigo_interno_adoptado=code, estado_interno='RESUELTO_INTERNO_DECISION_AUTORIZADA_F02',
         regla=decision['regla_id'], clasificacion='B/C/D; E fecha administrativa y atribución documental')
overlay['estado_despues'] = copy.deepcopy(u)
dump(Q / 'ADJUDICACION_INTERNA.json', overlay)
dump(Q / 'F02_OBSERVACIONES_ACTUALIZADAS.json', [x for x in updated if x['persona'] == person])
dump(Q / 'REVISION_IINF_Y_LOCALIZADORES.json', {'pendientes':new_plan,'contraejemplo_V3':contrast,
       'contexto':case,'cruces_2024':cohort})

def pending_counts(rows, field):
    q = [x for x in rows if not x[field]]
    return {'observaciones':len(q),'personas':len({x['persona'] for x in q})}

result = {'clasificacion':'B/C; D adjudicación autorizada; E pendientes',
    'F02':{'observaciones':9,'pendientes_antes':4,'cierres_internos_nuevos':1,'pendientes_despues':3,'resuelto_completo':False},
    'interno_antes':pending_counts(obs,'codigo_interno_adoptado'),
    'interno_despues':pending_counts(updated,'codigo_interno_adoptado'),
    'documental_antes':pending_counts(obs,'codigo_documental_atribuible'),
    'documental_despues':pending_counts(updated,'codigo_documental_atribuible'),
    'universo_conservado':{'personas':5901,'expedientes_referencia_aprobada':6622,'observaciones':24774},
    'cruce_IINF20241_O_2024':{'observaciones':len(cohort),'personas':len({x['persona'] for x in cohort}),
        'codigos_documentales':dict(counts),'personas_por_codigo_no_aditivas':{
        c:len({x['persona'] for x in cohort if x['codigo_documental_atribuible']==c}) for c in [code,'I162S2C1J4V3']},
        'limite':'Código anual atribuido por el diagnóstico; no fecha administrativa ni equivalencia universal'},
    'oferta_2024':offers,'equivalencias_plan_2026':equiv,'manual_FCU_IINF':manual_iinf,
    'pendiente_exacto':'Vincular IINF20241 de F02 en 2024/1–3 con una versión aplicable. El dato MU con fecha coincidente apunta al expediente anterior. No extrapolar el catálogo 2026 ni usar mayoría del plan.',
    'candidato_no_adoptado_IINF':code,
}
qa = {'estado':'OK_CON_ADVERTENCIAS', 'observaciones_unicas':len({x['observacion_id'] for x in obs})==len(obs),
    'un_solo_cambio_autorizado':sum(a!=b for a,b in zip(obs,updated))==1,
    'documental_identico':all(a['codigo_documental_atribuible']==b['codigo_documental_atribuible'] for a,b in zip(obs,updated)),
    'universo_identico':len(obs)==len(updated)==24774 and len({x['persona'] for x in updated})==5901,
    'referencias_MU_releidas':len(checks), 'tres_pendientes_no_promovidas':all(not x['codigo_interno_adoptado'] for x in updated if x['persona']==person and x['plan']=='IINF20241'),
    'entradas_intactas':all(sha(p)==h for p,h in hashes.items()), 'privado_fuera_git':True,
    'limite':'Cierre interno aplicado en capa separada; tres observaciones E y fecha administrativa pendiente. No recalcula tasas.'}
assert all(v for v in qa.values() if isinstance(v,bool))
assert result['interno_despues']=={'observaciones':3093,'personas':1751}
assert result['documental_despues']=={'observaciones':3213,'personas':1838}
dump(O / 'DECISION.json', decision)
dump(O / 'RESULTADOS.json', result)
dump(O / 'QA.json', qa)
dump(O / 'FUENTES_HASHES.json', hashes)
report = '''# F02: cierre interno y revisión IINF20241

**D/C:** se aplicó el cierre autorizado de IECIREOL20211, 2024/2 bimestral,
como I162S2C1J4V2 en una adjudicación separada. No se altera la base original
ni se declara envío SIES acreditado. Responsable: Alexi; ejecución: Codex.

| Observación | Código interno tras revisión | Estado | Clase |
|---|---|---|---|
| IECIREOL20211, 2024/2 bimestral | I162S2C1J4V2 | Cerrada internamente por autorización | B/C/D |
| IINF20241, 2024/T1 | Pendiente; candidato V2 | Falta atribución al expediente/período | B/C/E |
| IINF20241, 2024/T2 | Pendiente; candidato V2 | Falta atribución al expediente/período | B/C/E |
| IINF20241, 2024/T3 | Pendiente; candidato V2 | Plan confirmado por respaldo T3; versión pendiente | B/C/E |

## Qué aportan los cruces gobernados

**B/C:** IINF20241, carrera IINF, jornada 4, año 2024 reúne 403 observaciones
de 171 personas en el diagnóstico. Hay 330 observaciones atribuidas a V2
(132 personas), tres a V3 (una persona) y 70 pendientes. No se infiere una
equivalencia universal por mayoría. Se releyó la referencia MU del caso V3
y la de F02, corroborando identidad, año y código. El contraejemplo no prueba
que F02 sea V3: demuestra que el plan y jornada solos no distinguen versión.

**B:** la oferta 2024 contiene V2 regular de ocho semestres y V3 continuidad
de cuatro, esta última sin admisión nueva declarada. El catálogo de grupo
operativo 2026 propone V2 para IINF/RE/O; su maestro deja la equivalencia
del plan sin vigencia acreditada y no habilitada para resolver. No hay fila
IINF en las equivalencias manuales FCU2026 consultadas. No se retrotrae esa
relación operativa a 2024.

**B/C:** para F02, la fecha MU2024 coincide exclusivamente con el expediente
IECIREOL (22-abril), mientras IINF declara 24-abril. Los respaldos acreditan
IINF20241 por período, pero no añaden una versión SIES vinculada al nuevo
expediente. V2 se conserva como candidato para las tres observaciones; no se
confunde la corroboración anual de la persona con un enlace a ambos expedientes.

**E:** no se resolvió completamente F02. No se exige el día administrativo
como condición universal; falta la atribución de versión al nuevo expediente
en los tres períodos de 2024. El día del cambio queda como pendiente separado.

## Efecto y conservación

**C:** pendientes internos: 3.094 → 3.093 observaciones. Personas con algún
pendiente: 1.751 → 1.751, porque F02 conserva tres. Pendientes documentales:
3.213 observaciones y 1.838 personas, sin cambios. F02: cuatro → tres
observaciones pendientes; cinco observaciones de 2023 ya estaban resueltas.

**D:** denominadores, bases, libros, fuentes y motor anual conservados. El
universo aprobado permanece 5.901 personas / 6.622 expedientes / 24.774
observaciones; no se cambia el grano de expediente. No se recalculan tasas.

**C:** QA OK_CON_ADVERTENCIAS: una sola modificación interna autorizada al
aplicar la adjudicación en memoria, ninguna documental, fuentes intactas,
identificadores en detalle privado fuera de Git. DECISION.json conserva
responsable, fecha/hora, alcance y reversión. MANIFEST.json incluye rutas y
hashes. Esta entrega local no está publicada: sin commit/push.

Reanudación: cargar OBSERVACIONES_PRIVADAS.json con el hash de entrada y
superponer únicamente ADJUDICACION_INTERNA.json por observacion_id, comprobando
estado_antes. El script reproduce los resultados y conserva los diagnósticos
anteriores. No trasladar la decisión a otros expedientes ni a un motor productivo.
'''
(O / 'INFORME.md').write_text(report)
after_git = git()
assert (before_git['rama'],before_git['head'],before_git['remotos']) == (after_git['rama'],after_git['head'],after_git['remotos'])
dump(O / 'GIT_DESPUES.json', after_git)
# Revisión de privacidad de salidas compartibles: no RUT ni CODCLI del caso.
secrets = {person, person.split('-')[0], *[x['CODCLI'] for x in f]}
for path in O.iterdir():
    if path.is_file():
        text = path.read_text()
        assert all(not s or s not in text for s in secrets), 'Identificador en salida compartible'
dump(O / 'MANIFEST.json', {'fecha_hora':now.isoformat(),'proceso':'Puente UMAS–SIES IPSS162, F02/2024',
     'clasificacion':'B/C/D; E pendientes','salida':str(O),'privado':str(Q),
     'fuentes_hashes':hashes,'salidas_hashes':{p.name:sha(p) for p in O.iterdir() if p.is_file()},
     'privados_hashes':{p.name:sha(p) for p in Q.iterdir()},'resultado':result['F02'],
     'qa':qa,'rama':after_git['rama'],'HEAD':after_git['head'],'commit_push':False})
print(json.dumps({'salida':str(O),'privado':str(Q),'resultado':result['F02'],'QA':qa['estado'],'informe_sha256':sha(O/'INFORME.md')},ensure_ascii=False))
