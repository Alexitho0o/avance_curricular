"""Extract an ordered question/option inventory from LimeSurvey LSG or LSS exports."""
import argparse
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TYPE_LABELS = {
    'L':'Selección única', '!':'Lista desplegable', 'M':'Selección múltiple',
    'P':'Selección múltiple con comentarios', 'F':'Matriz con escala configurable',
    'A':'Matriz de 5 puntos', 'B':'Matriz de 10 puntos', 'H':'Matriz por columnas',
    ':':'Matriz de doble escala', 'Y':'Sí/No', 'S':'Texto corto', 'T':'Texto largo',
    'U':'Texto muy largo', 'N':'Número', 'D':'Fecha', 'Q':'Textos múltiples',
    'K':'Números múltiples', 'X':'Texto informativo', 'R':'Ordenación',
    '*':'Ecuación', 'G':'Género', 'I':'Cambio de idioma', '|':'Archivo'
}


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script','style'}:
            self.hidden += 1
        elif not self.hidden and tag in {'br','p','div','li','tr'}:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in {'script','style'}:
            self.hidden = max(0, self.hidden-1)
        elif not self.hidden and tag in {'p','div','li','tr'}:
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain(value):
    parser = PlainText()
    parser.feed(value or '')
    text = ''.join(parser.parts).replace('\xa0',' ')
    return '\n'.join(line for line in (re.sub(r'\s+', ' ', x).strip() for x in text.splitlines()) if line)


def rows(root, table):
    return [{child.tag:child.text or '' for child in row} for row in root.findall(f'./{table}/rows/row')]


def numeric(value, default=0):
    return int(value) if str(value).lstrip('-').isdigit() else default


def localized(records, key, language):
    output = {}
    for item in records:
        if item.get('language',language) != language:
            continue
        identity = item[key]
        if identity in output:
            raise ValueError(f'Duplicate localized identity: {key}={identity}')
        output[identity] = item
    return output


def builtin_options(kind, language):
    if kind == 'Y':
        labels = ['Sí','No'] if language == 'es' else ['Yes','No']
        return [{'code':code, 'text':label, 'scale':'', 'origin':'Tipo LimeSurvey'}
                for code,label in zip(['Y','N'],labels)]
    if kind in {'A','B'}:
        count = 5 if kind == 'A' else 10
        return [{'code':str(n), 'text':str(n), 'scale':'', 'origin':'Tipo LimeSurvey'} for n in range(1,count+1)]
    return []


def parse_exports(paths, language='es'):
    groups, sources, surveys = [], [], set()
    seen_groups, seen_questions, seen_qids = set(), set(), set()
    for path in paths:
        path = Path(path).expanduser().resolve()
        content = path.read_bytes()
        root = ET.fromstring(content)
        languages = [node.text for node in root.findall('./languages/language')]
        if languages and language not in languages:
            raise ValueError(f'{path.name}: no contiene idioma {language}.')
        group_texts = localized(rows(root,'group_l10ns'), 'gid', language)
        question_texts = localized(rows(root,'question_l10ns'), 'qid', language)
        answer_texts = localized(rows(root,'answer_l10ns'), 'aid', language)
        question_rows = rows(root,'questions')
        children = rows(root,'subquestions') + [
            q for q in question_rows if q.get('parent_qid','0') not in {'','0'}
            and q.get('language',language) == language]
        parents = [q for q in question_rows if q.get('parent_qid','0') in {'','0'}
                   and q.get('language',language) == language]
        answers = [a for a in rows(root,'answers') if a.get('language',language) == language]
        attributes = rows(root,'question_attributes')
        for g in rows(root,'groups'):
            if g.get('language',language) != language:
                continue
            identity = (g['sid'],g['gid'])
            if identity in seen_groups:
                raise ValueError(f'Grupo duplicado {identity}: selecciona una sola exportacion por grupo.')
            seen_groups.add(identity)
            surveys.add(g['sid'])
            group = {'id':g['gid'], 'survey_id':g['sid'], 'order':numeric(g.get('group_order')),
                     'text':plain(group_texts.get(g['gid'],{}).get('group_name',g.get('group_name',''))),
                     'source':path.name, 'questions':[]}
            for parent in sorted((q for q in parents if q['gid']==g['gid']), key=lambda q:numeric(q.get('question_order'))):
                code, qid = parent['title'], parent['qid']
                if code in seen_questions or qid in seen_qids:
                    raise ValueError(f'Pregunta duplicada: {code} / {qid}. No combinar versiones.')
                seen_questions.add(code)
                seen_qids.add(qid)
                localized_parent = question_texts.get(qid,{})
                subs = []
                for sub in sorted((s for s in children if s['parent_qid']==qid), key=lambda s:(numeric(s.get('scale_id')),numeric(s.get('question_order')))):
                    sub_text = question_texts.get(sub['qid'],{}).get('question',sub.get('question',''))
                    subs.append({'code':sub['title'], 'text':plain(sub_text),
                                 'scale':sub.get('scale_id','0'), 'order':numeric(sub.get('question_order'))})
                if len({(s['code'],s['scale']) for s in subs}) != len(subs):
                    raise ValueError(f'{code}: subpreguntas repetidas en una escala.')
                options = []
                for option in sorted((a for a in answers if a['qid']==qid), key=lambda a:(numeric(a.get('scale_id')),numeric(a.get('sortorder')))):
                    label = answer_texts.get(option.get('aid',''),{}).get('answer',option.get('answer',''))
                    options.append({'code':option['code'], 'text':plain(label),
                                    'scale':option.get('scale_id','0'), 'origin':'Archivo LSG/LSS'})
                if len({(a['code'],a['scale']) for a in options}) != len(options):
                    raise ValueError(f'{code}: opciones repetidas en una escala.')
                attrs = {a['attribute']:a.get('value','') for a in attributes if a['qid']==qid
                         and a.get('language',language) in {'',language}}
                kind = parent['type']
                question = {'id':qid, 'code':code, 'type':kind, 'type_label':TYPE_LABELS.get(kind,f'Tipo LimeSurvey {kind}'),
                            'order':numeric(parent.get('question_order')),
                            'text':plain(localized_parent.get('question',parent.get('question',''))),
                            'help':plain(localized_parent.get('help',parent.get('help',''))),
                            'relevance':parent.get('relevance',''),
                            'other':parent.get('other')=='Y', 'attributes':attrs,
                            'subquestions':subs, 'options':options,
                            'builtin_options':builtin_options(kind,language) if not options else []}
                group['questions'].append(question)
            groups.append(group)
        sources.append({'path':str(path), 'filename':path.name, 'sha256':hashlib.sha256(content).hexdigest()})
    if len(surveys) != 1:
        raise ValueError('Los archivos deben corresponder a una sola encuesta, sin mezclar anos/versiones.')
    groups.sort(key=lambda g:g['order'])
    for group_index, group in enumerate(groups,1):
        group['position'] = group_index
        for question_index, question in enumerate(group['questions'],1):
            question['position_in_group'] = question_index
    return {'survey_id':next(iter(surveys)), 'language':language, 'groups':groups, 'sources':sources}


def summarize(items, label, limit=12):
    if len(items) > limit or sum(len(item['text']) for item in items)>550:
        return f'{len(items)} {label}. Lista completa en Detalle.'
    return '\n'.join(f'{item["code"]}: {item["text"]}' for item in items)


def workbook_tables(instrument):
    questions, detail = [], []
    order = 0
    for group in instrument['groups']:
        for q in group['questions']:
            order += 1
            options = q['options'] or q['builtin_options']
            if q['type'] in {'M','P'}:
                response_summary = f'{len(q["subquestions"])} opciones de selección múltiple; ver Detalle.'
            elif options:
                response_summary = summarize(options,'opciones')
            elif q['type'] in {'S','T','U','Q','N','K','D','|'}:
                response_summary = q['type_label'] + ' (entrada libre)'
            elif q['type']=='X':
                response_summary = 'Texto informativo; no solicita respuesta'
            else:
                response_summary = 'Sin alternativas explícitas en el archivo'
            for attribute,label in [('min_answers','Mínimo de selecciones'),('max_answers','Máximo de selecciones'),
                                    ('min_num_value','Valor mínimo'),('max_num_value','Valor máximo'),
                                    ('maximum_chars','Máximo de caracteres')]:
                if q['attributes'].get(attribute,'').strip():
                    response_summary += '\n' + label + ': ' + q['attributes'][attribute]
            questions.append([order,group['text'],q['code'],q['text'],q['type_label'],response_summary,
                              summarize(q['subquestions'],'subpreguntas'), 'Sí' if q['other'] else 'No', group['source']])
            base = [order,group['text'],q['code'],q['text']]
            for sub in q['subquestions']:
                element = 'Opción múltiple' if q['type'] in {'M','P'} else 'Subpregunta'
                detail.append(base+[element,sub['code'],sub['text'],sub['scale'],'Archivo LSG/LSS',group['source']])
            for option in options:
                element = 'Opción de escala' if q['subquestions'] and q['type'] not in {'M','P'} else 'Opción'
                detail.append(base+[element,option['code'],option['text'],option['scale'],option['origin'],group['source']])
            if q['other']:
                label = plain(q['attributes'].get('other_replace_text','')) or ('Otro (especificar)' if instrument['language']=='es' else 'Other')
                detail.append(base+['Campo Otro','other',label,'','Campo Otro activado en el archivo',group['source']])
            if not q['subquestions'] and not options:
                detail.append(base+['Entrada libre' if q['type']!='X' else 'Texto informativo','',
                                    response_summary,'','Tipo de pregunta',group['source']])
    return {'Preguntas':{'headers':['Orden','Grupo LimeSurvey','Código pregunta','Pregunta','Tipo de respuesta',
                                   'Respuestas posibles','Subpreguntas','Campo Otro','Fuente LSG/LSS'], 'rows':questions},
            'Detalle':{'headers':['Orden pregunta','Grupo LimeSurvey','Código pregunta','Pregunta','Elemento',
                                 'Código elemento','Texto de opción/subpregunta','Escala','Origen del elemento','Fuente LSG/LSS'],
                       'rows':detail}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anio', type=int, required=True)
    parser.add_argument('--periodo', type=int, choices=[1,2,3], default=1)
    parser.add_argument('--entrada', type=Path, default=Path.home()/'Downloads')
    parser.add_argument('--patron', default='*.lsg')
    parser.add_argument('--archivos', nargs='+', type=Path)
    parser.add_argument('--idioma', default='es')
    parser.add_argument('--salida', type=Path)
    parser.add_argument('--solo-json', action='store_true')
    args = parser.parse_args()
    paths = args.archivos or sorted(args.entrada.expanduser().glob(args.patron))
    if not paths:
        parser.error('No se encontraron exportaciones para el patron/carpeta indicado.')
    from gobernanza.verificar_separacion_fcu import assert_frozen_reference, assert_2027_output_path
    assert_frozen_reference()
    instrument = parse_exports(paths,args.idioma)
    profile_path = ROOT/'docs/gobernanza/COMANDOS_OPERATIVOS.json'
    if profile_path.exists():
        profile = json.loads(profile_path.read_text())['financiamiento']
        if instrument['survey_id']==profile['survey_id'] and (args.anio,args.periodo)!=(profile['anio'],profile['periodo']):
            parser.error('Esta encuesta esta identificada en el proyecto como 2027 P1. Usa los exports del ano/periodo indicado, sin relabelar los actuales.')
    stamp = datetime.now(ZoneInfo('America/Santiago')).strftime('%Y%m%d')
    output = (args.salida or Path.home()/'Desktop'/f'Preguntas_y_respuestas_LimeSurvey_{args.anio}_P{args.periodo}_{stamp}.xlsx').expanduser().resolve()
    assert_2027_output_path(output)
    if output.exists():
        parser.error(f'La salida ya existe; elige otro nombre para conservar la version: {output}')
    instrument.update(year=args.anio,period=args.periodo,created=stamp)
    tables = workbook_tables(instrument)
    payload = {'instrument':instrument,'tables':tables}
    output.parent.mkdir(parents=True,exist_ok=True)
    if args.solo_json:
        target = output.with_suffix('.json')
        if target.exists():
            parser.error(f'La salida JSON ya existe: {target}')
        target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
        print(str(target))
        return
    runtime = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
    node = Path(os.environ.get('LIMESURVEY_NODE', str(runtime/'bin/node')))
    modules = Path(os.environ.get('LIMESURVEY_NODE_MODULES',str(runtime/'node_modules')))
    if not node.is_file() or not (modules/'@oai/artifact-tool').exists():
        parser.error('No se encontro Artifact Tool. Configura LIMESURVEY_NODE y LIMESURVEY_NODE_MODULES con el runtime disponible, o usa --solo-json.')
    builder = ROOT/'scripts/exportar_instrumento_limesurvey.mjs'
    digest = hashlib.sha256(''.join(s['sha256'] for s in instrument['sources']).encode()).hexdigest()[:12]
    evidence = ROOT/'.local/inventarios_limesurvey'/str(args.anio)/f'P{args.periodo}'/f'{instrument["survey_id"]}_{stamp}_{digest}'
    source_dir = evidence/'fuentes'
    source_dir.mkdir(parents=True,exist_ok=True)
    for source in instrument['sources']:
        target = source_dir/source['filename']
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError(f'Conflicting source snapshot: {target}')
        shutil.copy2(source['path'],target)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError('Source changed during snapshot; repeat with a stable export.')
        source['snapshot'] = str(target)
    (evidence/'inventory.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='inventario_limesurvey_') as temp:
        temp = Path(temp)
        if os.name=='nt':
            subprocess.run(['cmd','/c','mklink','/J',str(temp/'node_modules'),str(modules)],check=True,capture_output=True)
        else:
            (temp/'node_modules').symlink_to(modules,target_is_directory=True)
        copied = temp/builder.name
        shutil.copy2(builder,copied)
        subprocess.run([str(node),str(copied),str(evidence/'inventory.json'),str(output),str(evidence/'previews')],check=True)
    assert_frozen_reference()
    counts = {'groups':len(instrument['groups']), 'questions':sum(len(g['questions']) for g in instrument['groups']),
              'subquestions':sum(len(q['subquestions']) for g in instrument['groups'] for q in g['questions']),
              'explicit_options':sum(len(q['options']) for g in instrument['groups'] for q in g['questions'])}
    manifest = {'date':stamp,'year':args.anio,'period':args.periodo,'survey_id':instrument['survey_id'],
                'output':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
                'counts':counts,'sources':instrument['sources'],
                'scripts':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in [Path(__file__),builder]},
                'rule':'Year/period are explicit labels; use the exports of the corresponding instrument. Sources and the closed FCU 2026 are not modified.'}
    (evidence/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(output),'evidence':str(evidence),**counts},ensure_ascii=False))


if __name__=='__main__':
    main()
