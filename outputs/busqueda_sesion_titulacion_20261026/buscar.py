"""Busca etiquetas en sesiones locales del proyecto sin exportar conversaciones."""
import collections
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOTS = [Path('/Users/alexi/.codex/sessions'), Path('/Users/alexi/.codex/archived_sessions')]
PROJECT = '/Users/alexi/.codex/.chatgpt-projects/g-p-69c4286b2e4481919d68cf334acd0c21'
REPOSITORY = '/Users/alexi/Documents/GitHub/avance_curricular'
CURRENT = '01a0cc92-0df8-7720-8c55-f9007207cb98'
TERMS = ['TRACE_SCORE_CANDIDATO', 'TRACE_REASONS_CANDIDATO', 'Res_Tit_Unificada']
counts = collections.Counter()
for root in ROOTS:
    if not root.is_dir():
        counts['raices_no_accesibles'] += 1
        continue
    for path in root.rglob('*.jsonl'):
        try:
            with path.open(encoding='utf-8') as f:
                meta = json.loads(f.readline()).get('payload', {})
                cwd = str(meta.get('cwd', ''))
                sid = str(meta.get('id') or meta.get('session_id') or '')
                if not (cwd == PROJECT or cwd == REPOSITORY or cwd.startswith(REPOSITORY + '/')):
                    continue
                if sid == CURRENT:
                    counts['sesion_actual_excluida'] += 1
                    continue
                counts['sesiones_del_ambito_leidas'] += 1
                hit = False
                for line in f:
                    if any(t.casefold() in line.casefold() for t in TERMS):
                        hit = True
                if hit: counts['sesiones_con_mencion_literal'] += 1
        except (OSError, UnicodeError, ValueError):
            counts['archivos_con_error_lectura_o_metadatos'] += 1
out = {'clasificacion': 'C búsqueda literal; E origen desconocido',
       'raices': [str(x) for x in ROOTS], 'ambito': [PROJECT, REPOSITORY],
       'terminos': TERMS, 'conteos': dict(counts),
       'limitaciones': 'Solo JSONL locales accesibles con cwd coincidente; excluye sesión actual. No revisa sesiones cloud, otras aplicaciones, archivos con otro cwd ni variantes de las etiquetas. No exporta conversaciones ni identificadores personales.'}
(OUT / 'RESULTADO_AGREGADO.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(out, ensure_ascii=False))
