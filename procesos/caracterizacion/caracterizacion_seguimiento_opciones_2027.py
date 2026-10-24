"""Versioned option follow-up shared by the Word and action workbooks."""
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unicodedata

import pandas as pd

import caracterizacion_runtime as rt

ROOT = Path(__file__).resolve().parent
PROFILE = ROOT / 'gobernanza/instrumentos_limesurvey/2027/P1/141234_20261009_406d959cedfd'
POLICY = 'SEGUIMIENTO_OPCIONES_2027_P1-v2'
COMPANY_RESPONSE_FIELD = 'EMPRESA_O_EMPRENDIMIENTO_DECLARADO'
COMPANY_STATUS_FIELD = 'ESTADO_NOMBRE_EMPRENDIMIENTO'
COMPANY_RULE = ('G02Q27 es una pregunta institucional mixta de empresa o emprendimiento. '
                'Su respuesta literal no confirma el nombre de un emprendimiento propio. '
                'El filtro del instrumento versionado solo incluye G02Q95 AO01/AO02, no AO05.')
MISSING = {'', 'NA', 'N/A', 'NAN', 'NAT', 'NULL', 'NONE', '-', '--', '.', 'S/I', 'SIN INFO'}
DETAIL_COLUMNS = ['TOKEN','RUT','NOMBRE','NOMBRE_L','SEDE','MAIL_INST','FONOACTUAL',
                  'ID_SEGUIMIENTO','CODIGO','CODIGO_ALTERNATIVA','CATEGORÍA','PREGUNTA','DETALLE',
                  'RESPUESTA','FECHA_ENVIO','RESPONDIO_HOY','MATRICULA_EN_VENTANA','ESTADO_RESPUESTA',
                  COMPANY_RESPONSE_FIELD,'MAIL',COMPANY_STATUS_FIELD]


def norm(value):
    if value is None or pd.isna(value):
        return ''
    value = unicodedata.normalize('NFKD', str(value))
    return re.sub(r'\s+', ' ', ''.join(c for c in value if not unicodedata.combining(c))).strip().upper()


def has_value(value):
    return norm(value) not in MISSING


def short_question(text):
    question = re.search(r'¿[^¿]+\?\s*$', text)
    return question.group(0).strip() if question else text


@lru_cache(maxsize=1)
def instrument():
    path = PROFILE / 'inventory.json'
    manifest = json.loads((PROFILE / 'manifest.json').read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['files']['inventory.json']:
        raise ValueError('Cambio el instrumento versionado; no relabelar los datos con otro catalogo.')
    return json.loads(path.read_text())['instrument']


def company_name_context():
    group, question = next((g, q) for g in instrument()['groups'] for q in g['questions']
                           if q['code'] == 'G02Q27')
    return {'code':question['code'], 'question':question['text'], 'group':group['text'],
            'type':question['type'], 'relevance':question['relevance'], 'origin':'INSTITUCIONAL',
            'output_field':COMPANY_RESPONSE_FIELD, 'status_field':COMPANY_STATUS_FIELD,
            'confirms_business_name':False, 'rule':COMPANY_RULE}


def company_name_status(value, column_present):
    if not column_present:
        return 'COLUMNA_AUSENTE'
    return 'NO_CONFIRMADO_PREGUNTA_MIXTA' if has_value(value) else 'SIN_RESPUESTA_G02Q27'


def monitoring_definitions():
    questions = {q['code']:q for g in instrument()['groups'] for q in g['questions']}
    groups = {q['code']:g['text'] for g in instrument()['groups'] for q in g['questions']}
    result = []
    def add(category, parent, code=None, label=None, rule='yes', answer_code=''):
        q = questions[parent]
        column = code or parent
        identity = column + ('::' + answer_code if answer_code else '')
        result.append({'id':identity, 'category':category, 'parent':parent, 'column':column,
            'answer_code':answer_code, 'question':q['text'], 'label':label or short_question(q['text']),
            'group':groups[parent], 'rule':rule, 'options':q['options'] or q['builtin_options']})
    add('Discapacidad','G01Q82')
    for sub in questions['G01Q17']['subquestions']:
        label = sub['text'].split(' (',1)[0].removeprefix('Sí, ')
        add('Discapacidad','G01Q17',f'G01Q17[{sub["code"]}]',label,'severity')
    add('Discapacidad','G01Q30')
    add('NEE','G01Q64')
    for sub in questions['G01Q65']['subquestions']:
        add('NEE','G01Q65',f'G01Q65[{sub["code"]}]',sub['text'],'checkbox')
    if questions['G01Q65']['other']:
        add('NEE','G01Q65','G01Q65[other]','Otra dificultad NEE informada','text')
    add('Salud de larga duración','G06Q61')
    add('Salud de larga duración','G06Q90',label='¿Qué condición de salud de larga duración?',rule='text')
    add('Pueblos originarios','G01Q75')
    add('Pueblos originarios','G01Q05',rule='answered')
    if questions['G01Q05']['other']:
        add('Pueblos originarios','G01Q05','G01Q05[other]','Otro pueblo originario informado','text')
    for sub in questions['G01Q19']['subquestions']:
        add('Financiamiento','G01Q19',f'G01Q19[{sub["code"]}]',sub['text'],'checkbox')
    add('VCM','G02Q95',label='Tengo un emprendimiento formalizado',rule='answer',answer_code='AO05')
    return result


def positive_value(value, definition):
    if not has_value(value):
        return False
    key = norm(value)
    rule = definition['rule']
    if rule == 'text':
        return True
    if rule == 'checkbox':
        if key in {'SI','Y','1','1.0','TRUE'}:
            return True
        if key in {'NO','N','0','0.0','FALSE'}:
            return False
        raise ValueError(f'Respuesta multiple no reconocida en {definition["column"]}.')
    choices = {norm(o['code']):norm(o['text']) for o in definition['options']}
    choices.update({norm(o['text']):norm(o['text']) for o in definition['options']})
    if rule == 'answer':
        positive = {
            norm(o[key_name]) for o in definition['options'] if o['code'] == definition['answer_code']
            for key_name in ['code','text']}
        if key not in choices:
            raise ValueError(f'Alternativa no reconocida en {definition["column"]}.')
        return key in positive
    if rule == 'yes' and key in {'SI','Y','TRUE','1','1.0'}:
        return True
    if rule == 'yes' and key in {'NO','N','FALSE','0','0.0'}:
        return False
    if key not in choices and not (rule == 'answered' and key in {'OTRO','OTHER','-OTH-'}):
        raise ValueError(f'Alternativa no reconocida en {definition["column"]}.')
    if rule == 'answered':
        return True
    if rule == 'severity':
        return choices[key] in {'LEVE','MODERADA','SEVERA'}
    return choices[key] == 'SI'


def active_category_codes():
    categories, labels = {}, {}
    for item in monitoring_definitions():
        categories.setdefault(item['category'], []).append(item['column'])
        labels[item['column'].upper()] = item['label']
    return categories, labels


def positive_mask(series, code):
    found = [d for d in monitoring_definitions() if d['column'].upper() == code.upper()]
    if len(found) != 1:
        raise ValueError('Codigo de seguimiento sin una definicion unica: ' + code)
    return series.map(lambda value:positive_value(value,found[0])).astype(bool)


def column_code(name):
    match = re.match(r'^(G\d+Q\d+(?:\[[^\]]+\])?)(?:\.|\s|$)', str(name).strip(), re.I)
    return match.group(1).upper() if match else None


def submit_timestamp(value):
    if not has_value(value):
        return None
    timestamp = pd.to_datetime(value, errors='coerce')
    if pd.isna(timestamp):
        return None
    return timestamp.tz_localize(rt.TZ_NAME) if timestamp.tzinfo is None else timestamp.tz_convert(rt.TZ_NAME)


def compute_followup(target, results, cutoff, *, columns=None, responses_available=True, window=None):
    definitions = monitoring_definitions()
    columns = columns or {}
    target = target.copy()
    token_field = next((c for c in ['_token_match','TOKEN','_token_norm'] if c in target), None)
    if token_field is None or target[token_field].duplicated().any():
        raise ValueError('El objetivo de seguimiento necesita una fila por token.')
    target[token_field] = target[token_field].astype(str)
    lookup = target.set_index(token_field)
    source = results.copy()
    result_token = next((c for c in ['_token_norm','_token_match','TOKEN','token'] if c in source), None)
    if result_token is None:
        matches = [c for c in source if str(c).lower().startswith('token.')]
        result_token = matches[0] if len(matches) == 1 else None
    if result_token is None and not source.empty:
        raise ValueError('No se encontro token canonico en las respuestas.')
    if result_token:
        source = source.loc[source[result_token].astype(str).isin(lookup.index)].copy()
        if source[result_token].astype(str).duplicated().any():
            raise ValueError('El seguimiento debe recibir respuestas canonicas, sin tokens duplicados.')
    code_columns = {}
    for column in source:
        code = column_code(column)
        if code:
            if code in code_columns:
                raise ValueError('Columnas de pregunta ambiguas: ' + code)
            code_columns[code] = column
    submit_column = next((c for c in ['_SUBMITDATE_DT','submitdate'] if c in source), None)
    if submit_column is None:
        matches = [c for c in source if str(c).lower().startswith('submitdate.')]
        submit_column = matches[0] if len(matches) == 1 else None
    if responses_available and not source.empty and submit_column is None:
        raise ValueError('Falta submitdate para distinguir Acumulado y Hoy.')
    dates = {index:submit_timestamp(row[submit_column]) if submit_column else None for index,row in source.iterrows()}
    raw_submit = next((c for c in source if str(c).lower()=='submitdate' or str(c).lower().startswith('submitdate.')),submit_column)
    if any(value is not None and value.date() > cutoff for value in dates.values()):
        raise ValueError('Existen respuestas posteriores al corte solicitado.')
    company_context = company_name_context()
    company_column = code_columns.get(company_context['code'])
    metrics, details, raw_rows = [], [], []
    for index, row in source.iterrows():
        timestamp = dates[index]
        raw_value = row[raw_submit] if raw_submit else None
        raw = {'TOKEN':str(row[result_token]),
               'SUBMITDATE_ORIGINAL':None if raw_value is None or pd.isna(raw_value) else str(raw_value),
               'FECHA_ENVIO':timestamp.tz_localize(None).isoformat() if timestamp is not None else None}
        for item in definitions:
            column = code_columns.get(item['column'].upper())
            raw[item['column']] = None if column is None or pd.isna(row[column]) else str(row[column])
        raw[company_context['code']] = (
            None if company_column is None or pd.isna(row[company_column]) else str(row[company_column]))
        raw_rows.append(raw)
    for item in definitions:
        column = code_columns.get(item['column'].upper())
        state = 'DISPONIBLE' if column is not None else ('SIN_RESPUESTAS' if not responses_available else 'COLUMNA_AUSENTE')
        selected = []
        answered = 0
        if column is not None:
            for index, row in source.iterrows():
                value = row[column]
                answered += int(has_value(value))
                if positive_value(value,item):
                    selected.append((index,row))
        today_count = sum(dates[index] is not None and dates[index].date() == cutoff for index,_ in selected)
        metric = {**{k:item[k] for k in ['id','category','column','answer_code','question','label','group']},
                  'total':len(selected) if column is not None else None,
                  'today':int(today_count) if column is not None else None,
                  'answered':answered, 'state':state, 'source_column':column}
        metrics.append(metric)
        for index, row in selected:
            token = str(row[result_token])
            student = lookup.loc[token]
            def get(name, fallback=None):
                field = columns.get(name, fallback or name)
                value = student.get(field)
                return None if value is None or pd.isna(value) else str(value).strip()
            timestamp = dates[index]
            date_enrollment = pd.to_datetime(get('FECHAMATRICULA'),dayfirst=True,errors='coerce')
            in_window = bool(window and pd.notna(date_enrollment) and window[0] <= date_enrollment.date() <= window[1])
            company_value = row[company_column] if company_column is not None else None
            details.append({'TOKEN':token,'RUT':get('RUT'),'NOMBRE':get('NOMBRE'),
                'NOMBRE_L':get('NOMBREL','NOMBRE_L'),'SEDE':get('SEDE'), 'MAIL_INST':get('MAILINST','Mail_Inst'),
                'FONOACTUAL':get('FONOACTUAL'),'ID_SEGUIMIENTO':item['id'],'CODIGO':item['column'],
                'CODIGO_ALTERNATIVA':item['answer_code'], 'CATEGORÍA':item['category'],
                'PREGUNTA':item['question'],'DETALLE':item['label'],'RESPUESTA':str(row[column]),
                'FECHA_ENVIO':timestamp.tz_localize(None).isoformat() if timestamp is not None else None,
                'RESPONDIO_HOY':int(timestamp is not None and timestamp.date()==cutoff),
                'MATRICULA_EN_VENTANA':int(in_window),
                'ESTADO_RESPUESTA':row.get('estado_respuesta',student.get('Responden','')),
                COMPANY_RESPONSE_FIELD:None if pd.isna(company_value) else company_value,
                COMPANY_STATUS_FIELD:company_name_status(company_value, company_column is not None),
                'MAIL':get('MAIL')})
    detail = pd.DataFrame(details, columns=DETAIL_COLUMNS)
    vcm = detail.loc[detail['CATEGORÍA'].eq('VCM')].copy()
    retired = [
        {'anterior':code,'actual':None,'estado':'RETIRADA_EN_EXPORTACION_2027','explicacion':text}
        for code,text in [('G01Q31','Orientacion para registro de discapacidad'),
                          ('G06Q66','Participacion en PIE'),('G01Q06','Acreditacion CONADI')]]
    changes = [{'anterior':d['column'],'actual':d['column'],'estado':'ACTIVA',
                'explicacion':d['label']} for d in definitions]
    changes.extend(retired)
    return {'metrics':metrics,'detail':detail,'vcm':vcm,'raw':pd.DataFrame(raw_rows),
            'changes':changes,'cutoff':cutoff.isoformat(),'source_rows':len(source),
            'company_name_context':{**company_context, 'source_column':company_column},
            'vcm_name_status_counts':vcm[COMPANY_STATUS_FIELD].value_counts().to_dict(),
            'date_rule':'Hoy = submitdate en America/Santiago igual a la fecha del reporte. No se usa FECHAMATRICULA ni datestamp como fecha de envio.',
            'instrument_sha256':hashlib.sha256((PROFILE/'inventory.json').read_bytes()).hexdigest()}


def prepare_followup(namespace, plan, responses_available=True):
    target = namespace.get('df_vigentes',plan.eligible)
    data = compute_followup(target,namespace.get('df_resultados',pd.DataFrame()),plan.today,
        columns=plan.columns,responses_available=responses_available,window=plan.window)
    namespace['SEGUIMIENTO_OPCIONES_2027'] = data
    return data


def legacy_detail(data):
    frame = data['detail'].copy()
    return frame[['RUT','CODIGO','CATEGORÍA','DETALLE','RESPUESTA','NOMBRE_L','NOMBRE',
                  'FONOACTUAL','MAIL','MAIL_INST','RESPONDIO_HOY','FECHA_ENVIO']]


def workbook_payload(data, vcm=False):
    metrics = [m for m in data['metrics'] if not vcm or m['category']=='VCM']
    detail = data['vcm'] if vcm else data['detail']
    title = 'VCM Emprendimientos formalizados 2027 P1' if vcm else 'Seguimiento de opciones 2027 P1'
    summary = {'name':'Resumen','headers':['Categoria','ID seguimiento','Codigo Lime','Alternativa','Pregunta','Opcion','Acumulado','Hoy','Estado fuente'],
        'rows':[[m['category'],m['id'],m['column'],m['answer_code'],short_question(m['question']),m['label'],m['total'],m['today'],m['state']] for m in metrics],
        'widths':[24,27,24,15,55,50,14,14,25]}
    detail_sheet = {'name':'Emprendimientos' if vcm else 'Detalle', 'headers':list(detail.columns),
        'rows':json.loads(detail.to_json(orient='values',force_ascii=False)),
        'widths':[16,18,32,36,12,42,19,26,23,17,24,55,48,40,24,18,23,22,48,42,42],
        'date_columns':[14], 'preview_ranges':['S4:U'+str(min(10,len(detail)+4))]}
    raw = data['raw']
    if vcm:
        raw = raw.reindex(columns=['TOKEN','SUBMITDATE_ORIGINAL','FECHA_ENVIO','G02Q95','G02Q27'])
    raw_sheet = {'name':'Respuestas fuente','headers':list(raw.columns) or ['TOKEN','SUBMITDATE_ORIGINAL','FECHA_ENVIO'],
                 'rows':json.loads(raw.to_json(orient='values',force_ascii=False)),
                 'widths':[18,28,28]+[36]*max(0,len(raw.columns)-3),
                 'date_columns':[2],
                 'source_notes':[data['company_name_context']['question'], COMPANY_RULE]}
    sheets = [summary,detail_sheet,raw_sheet]
    if not vcm:
        sheets.append({'name':'Mapa 2027','headers':['Codigo anterior','Codigo actual','Estado','Seguimiento'],
            'rows':[[c['anterior'],c['actual'],c['estado'],c['explicacion']] for c in data['changes']], 'widths':[26,26,34,85]})
    return {'title':title,'cutoff':data['cutoff'],'date_rule':data['date_rule'],
            'detail_sheet':detail_sheet['name'], 'sheets':sheets,
            'source':'Cuestionario 141234 version 20261009 y respuestas actuales canonicas; solo estudiantes elegibles.'}


def export_artifact_workbook(payload, output, evidence, *, builder_name='exportar_seguimiento_opciones_2027.mjs'):
    runtime = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
    node = Path(os.environ.get('LIMESURVEY_NODE',str(runtime/'bin/node')))
    modules = Path(os.environ.get('LIMESURVEY_NODE_MODULES',str(runtime/'node_modules')))
    if not node.is_file() or not (modules/'@oai/artifact-tool').exists():
        raise ValueError('No se encontro Artifact Tool para los Excel de seguimiento. Configurar LIMESURVEY_NODE y LIMESURVEY_NODE_MODULES.')
    evidence.mkdir(parents=True,exist_ok=True,mode=0o700)
    model = evidence/'payload.json'
    model.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    model.chmod(0o600)
    builder = ROOT/'scripts'/builder_name
    with tempfile.TemporaryDirectory(prefix='seguimiento_2027_') as directory:
        temp = Path(directory)
        if os.name == 'nt':
            subprocess.run(['cmd','/c','mklink','/J',str(temp/'node_modules'),str(modules)],check=True,capture_output=True)
        else:
            (temp/'node_modules').symlink_to(modules,target_is_directory=True)
        shutil.copy2(builder,temp/builder.name)
        subprocess.run([str(node),str(temp/builder.name),str(model),str(output),str(evidence/'previews')],check=True)
    inspection = Path(str(output)+'.inspect.ndjson')
    if inspection.exists():
        shutil.move(inspection,evidence/'export_inspect.ndjson')
    return str(output)


def publish_followup(namespace):
    data = namespace.get('SEGUIMIENTO_OPCIONES_2027') or prepare_followup(namespace,namespace['INCORPORACION_PLAN'])
    stamp = data['cutoff'].replace('-','')
    names = {'categorias':f'Lista_tokens_categorias_SI_2027_P1_{stamp}.xlsx',
             'vcm':f'VCM_Emprendimientos_formalizados_2027_P1_{stamp}.xlsx'}
    evidence = ROOT/'.local/seguimiento_opciones_2027'/rt.get_context().run_dir.name
    outputs = {role:export_artifact_workbook(workbook_payload(data,role=='vcm'),
        rt.output_path(name,audit=False),evidence/role) for role,name in names.items()}
    namespace['df_categorias_si_vig'] = legacy_detail(data)
    namespace['SEGUIMIENTO_OPCIONES_SALIDAS_2027'] = outputs
    audit = {'policy':POLICY,'cutoff':data['cutoff'],'date_rule':data['date_rule'],
             'instrument_sha256':data['instrument_sha256'],'metrics':data['metrics'],'changes':data['changes'],
             'company_name_context':data['company_name_context'],
             'vcm_name_status_counts':data['vcm_name_status_counts'],
             'source_rows':data['source_rows'],'outputs':outputs,'personal_data_included':False}
    path = rt.output_path(f'CONTROL_SEGUIMIENTO_OPCIONES_2027_P1_{stamp}.json',audit=True)
    path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for metric in data['metrics']:
        print(f'[SEGUIMIENTO OPCIONES] codigo={metric["column"]}; alternativa={metric["answer_code"]}; acumulado={metric["total"]}; hoy={metric["today"]}; estado={metric["state"]}',flush=True)
    print('[SEGUIMIENTO OPCIONES] Excel de categorias y VCM disponibles en 02_SALIDAS.',flush=True)
    print('[VCM NOMBRE] G02Q27 conserva empresa/emprendimiento literal; no confirma un nombre propio. '
          + json.dumps(data['vcm_name_status_counts'],ensure_ascii=False),flush=True)
    return outputs
