"""Cierra la auditoría agregada sin modificar entradas, libros ni Git."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[2]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(name):
    return json.loads((OUT / name).read_text())


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args], text=True).strip()


chain = read('CADENA_Y_FUENTES.json')
universes = read('universos/RESULTADOS_UNIVERSOS.json')
lookup = read('llaves/QA.json')
corrections = read('correcciones/QA_Y_MANIFEST.json')
protected = []
for path, expected in chain['preservacion'].items():
    observed = sha(path)
    protected.append({'ruta': path, 'sha256_antes': expected,
                      'sha256_despues': observed, 'identico': observed == expected})

head = git('rev-parse', 'HEAD')
branch = git('branch', '--show-current')
tracked = git('status', '--porcelain', '--untracked-files=no')
staged = git('diff', '--cached', '--name-only')
files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.suffix in {'.json', '.md', '.py'})
syntax = []
for p in files:
    if p.suffix == '.py':
        ast.parse(p.read_text())
        syntax.append(str(p.relative_to(OUT)))

# Solo se registran cantidades de coincidencias; nunca se imprimen identidades.
private_path = Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase1_20261025/llaves/DETALLE_LLAVES.json')
private = json.loads(private_path.read_text())
identifiers = {str(x['documento_original']).strip() for x in private['detalle']}
identifiers = {s for s in identifiers if len(s) >= 6}
privacy = []
for p in files:
    content = p.read_text()
    tokens = set(re.findall(r'\b[A-Za-z0-9]+\b', content))
    exact = len(identifiers.intersection(tokens))
    rut = len(re.findall(r'(?<![\w])\d{7,8}-[\dkK](?![\w])', content))
    codcli = len(re.findall(r'\b(?:19|20)\d{2}[123][A-Z]{2,}\d{3,}\b', content))
    privacy.append({'archivo': str(p.relative_to(OUT)), 'documentos_exactos': exact,
                    'patrones_rut_dv': rut, 'patrones_codcli': codcli})
privacy_ok = all(not (x['documentos_exactos'] or x['patrones_rut_dv'] or x['patrones_codcli']) for x in privacy)

s = universes['seguimiento_diccionario']
controls = {
    'fuentes_10_disponibles_y_hash_coincidente': len(chain['fuentes']) == 10 and all(x['disponible'] and x['hash_coincide'] for x in chain['fuentes']),
    'protegidos_intactos': all(x['identico'] for x in protected),
    'rama_conservada': branch == chain['rama'],
    'HEAD_conservado': head == chain['HEAD'],
    'sin_archivos_preparados_commit': staged == '',
    'unico_cambio_tracked_previo': tracked == 'M PROYECTO_IPSS.json',
    'poblacion_grupo1_conservada': s['origenes'] == 3179,
    'posiciones_suman': s['con_contexto'] + s['sin_contexto'] == s['posiciones_2_periodos'] == 6358,
    'contextos_adicionales_explicados': s['con_contexto'] + s['adicionales_no_personas_nuevas'] == s['observaciones_contexto'] == 2854,
    'estados_contextos_suman': sum(s['estados_v18'].values()) == 2854,
    'agregado20_conserva_conteos': universes['v18_hoja20_agregada_conserva_conteos'],
    'sin_identificadores_detectados_entregables': privacy_ok,
}
ok = all(controls.values())
now = datetime.now(ZoneInfo('America/Santiago')).isoformat()
qa = {
    'clasificacion': 'B/C', 'fecha': now,
    'estado': 'PASS_CONTROLES_EJECUTADOS_CON_LIMITES' if ok else 'FALLIDO',
    'controles': controls, 'preservacion': protected,
    'rama_antes': chain['rama'], 'rama_despues': branch,
    'HEAD_antes': chain['HEAD'], 'HEAD_despues': head,
    'git_status_tracked': tracked, 'staged': staged,
    'sintaxis_scripts_correcta': syntax, 'revision_privacidad': privacy,
    'qa_especializados': {'llaves': lookup, 'correcciones_estado': corrections['estado']},
    'limites': [
        'No se ejecutó recálculo integral ni apertura Excel nativa.',
        'El contrato describe universos existentes; no aprueba cambios de alcance o denominador.',
        'La prueba anual no acredita aceptación SIES ni atribución CODCLI/plan en cada período.',
        'La revisión automática de privacidad cubre documentos del detalle auditado y patrones RUT/CODCLI; no es garantía universal por sí sola.',
    ], 'commit_push': False,
}
write('QA_FASE1.json', qa)
if not ok:
    raise SystemExit('QA FALLIDO: revisar controles agregados; no se cierra la fase.')

write('CHECKPOINT.json', {
    'clasificacion': 'C/D/E', 'fecha': now, 'fase': '1/6',
    'estado': 'EJECUTADA_CON_PENDIENTES_DE_ALCANCE',
    'hitos': [
        {'id': 'H1', 'estado': 'VERIFICADO', 'evidencia': 'CADENA_Y_FUENTES.json', 'resultado': '10 fuentes y maqueta formularia verificadas'},
        {'id': 'H2', 'estado': 'REPRODUCIDO_CON_E', 'evidencia': 'universos/RESULTADOS_UNIVERSOS.json', 'resultado': 'Padrones recuperados sin cambiar denominadores; etiqueta545/490, unidades y calendario explícitos'},
        {'id': 'H3', 'estado': 'VERIFICADO_EN_UNIVERSO_ANUAL', 'evidencia': 'llaves/QA.json', 'resultado': '2379 enlaces únicos, 0 discrepancias; 5 llaves múltiples fuera de ese universo'},
    ],
    'no_autorizado_en_esta_fase': ['cambiar bases', 'cambiar denominadores', 'cambiar libros', 'adjudicar códigos nuevos', 'commit', 'push'],
    'pendientes': [
        {'id': 'E01', 'tema': 'Alcance545grupo3-2026', 'detalle': 'TodoBase545personas vs ingreso2026-3 490. Mantener545; decidir etiqueta/alcance antes de cualquier redefinición.'},
        {'id': 'E02', 'tema': 'UnidadT2-2026', 'detalle': '528matrículas vs527personas;66renuncias sin nómina de origen. No convertir silenciosamente la tasa.'},
        {'id': 'E03', 'tema': 'Calendario', 'detalle': '6358posiciones son períodos nativos;2024se observa2025. No homologar cierres sin evidencia.'},
        {'id': 'E04', 'tema': 'Expedientes y atribución', 'detalle': 'Hoja20no tieneCODCLI;3520posiciones sin contexto no equivalen a deserción. Resolver enlaces en fases2–3.'},
        {'id': 'E05', 'tema': 'Cinco llavesMU2026', 'detalle': 'Diezfilas con códigos diferentes, fuera de2379cohortes auditadas. Conservar alternativas.'},
        {'id': 'E06', 'tema': 'Notas heredadas', 'detalle': '55!B11:104vs99;52!A32:v7vsv8. Actualizar en futura edición sin tocar cifras.'},
        {'id': 'E07', 'tema': 'Fuente primaria y retorno', 'detalle': 'Fase2 debe conectar envío/retorno y rol de cada fuente; coincidencia de componentes no es prueba de aceptación.'},
    ],
    'siguiente': 'Fase2/6 H1: enlace anual UMAS/expediente/MU y evidencia primaria; reutilizar los enlaces verificados. No ejecutada.',
    'HEAD': head,
})
manifest_files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.suffix in {'.md', '.json', '.py'} and p.name != 'MANIFEST_FASE1.json')
write('MANIFEST_FASE1.json', {
    'clasificacion': 'B/C/D/E', 'fecha': now, 'proceso': 'Trazabilidad integral UMAS–SIES / retención IPSS162',
    'fase': 1, 'estado': 'EJECUTADA_CON_PENDIENTES_DE_ALCANCE', 'repositorio': str(REPO),
    'rama': branch, 'HEAD_antes': chain['HEAD'], 'HEAD_despues': head,
    'plan': {'ruta': str(OUT.parent/'PLAN_FASES_HITOS.md'), 'sha256': sha(OUT.parent/'PLAN_FASES_HITOS.md')},
    'insumos_y_hashes': 'CADENA_Y_FUENTES.json y manifiestos de universos/correcciones/llaves',
    'salidas': [{'ruta': str(p.relative_to(REPO)), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in manifest_files],
    'detalle_privado': {'ruta': str(private_path), 'sha256': sha(private_path), 'fuera_git': True, 'publicar': False},
    'originales_intactos': True, 'denominadores_intactos': True, 'diccionario_activo_intacto': True,
    'nuevo_excel_generado': False, 'commit_push': False,
})
print(json.dumps({'estado': qa['estado'], 'controles_correctos': len(controls), 'archivos_manifestados': len(manifest_files), 'HEAD': head, 'informe_sha256': sha(OUT/'INFORME_FASE1.md'), 'manifest_sha256': sha(OUT/'MANIFEST_FASE1.json')}, ensure_ascii=False))
