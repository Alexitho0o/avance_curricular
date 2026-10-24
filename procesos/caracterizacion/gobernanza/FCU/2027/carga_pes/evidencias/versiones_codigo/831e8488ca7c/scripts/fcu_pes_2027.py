"""Independent FCU 2027 preparation and guarded CSV export. Never imports the 2026 pipeline."""
import argparse
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'gobernanza'))
import auditar_grupos_fcu_2027 as audit
from verificar_separacion_fcu import assert_frozen_reference, assert_2027_output_path, assert_private_output_path

MANUAL = audit.REFERENCE['MANUALS'][2027]
ENUM_REFERENCE = audit.BASE / 'json/AUDITORIA_ESTRUCTURA_20261007_ce05d9f5ce.json'
FIELD_WRAPS = {'CAMBIO_CIUDA': ('CAMBIO_CIUDAD', 'D'), 'CUIDADOS_CAN': ('CUIDADOS_CANT', 'T'),
               'NIVEL_EDU_PA': ('NIVEL_EDU_PADRE', 'DRE'), 'NIVEL_EDU_MA': ('NIVEL_EDU_MADRE', 'DRE'),
               'RAZ_NO_ARTIC': ('RAZ_NO_ARTICULA', 'ULA'), 'EST_PRE_TPCO': ('EST_PRE_TPCOM', 'M'),
               'EST_PRE_PFCO': ('EST_PRE_PFCOM', 'M'), 'EST_PRE_CAPC': ('EST_PRE_CAPCOM', 'OM')}
EXTERNAL = {'TIPO_DOC': 'Documento de identificacion validado; no inferir pasaporte/IPE desde el token.',
            'NRO_DOC': 'RUT con DV/documento en matricula. El token sin DV no reemplaza este dato.',
            'FECHA_NAC': 'FECHANACIMIENTO en matricula; fecha validada DD/MM/AAAA.',
            'CALLE': 'Calle estructurada. DIRECCIONACTUAL completa no equivale automaticamente a calle.',
            'NRO_CALLE': 'Numero de direccion estructurado; no extraer por una expresion ambigua.',
            'DEPTO_BLOCK': 'Departamento/block estructurado, si existe.',
            'REGION': 'Codigo oficial Anexo 4, no nombre ni inferencia desde la sede.',
            'COMUNA': 'Codigo oficial Anexo 5; COMUNAACTUAL requiere catalogo.',
            'CEL': 'FONOACTUAL/CELULAR: validar 11 digitos y prefijo 569.',
            'CORREO': 'MAIL personal validado; no sustituir silenciosamente por Mail_Inst.',
            'HOGAR_CANT': 'Conteos reales de hogar, incluyendo al estudiante; no sumar simples casillas 0/1.',
            'COD_INS': 'Codigo SIES institucional configurado, no inferido desde texto.',
            'COD_CAR': 'Codigo SIES completo de carrera, no CODCARPR ni CODCLI.'}


def schema_from_manual(path=MANUAL):
    lines = Path(path).read_text().splitlines()
    start = lines.index('6.2 Estructura de variables')
    end = lines.index('ANEXOS', start)
    anchors = []
    for i in range(start, end):
        match = re.match(r'^(?:[A-Z]{1,2} )?([A-Z][A-Z0-9_]{2,})\s+(.+)', lines[i])
        if match and re.search(r'Numéric|Cadena|Fecha', match[2]):
            anchors.append((i, match[1]))
    fields = []
    for n, (i, token) in enumerate(anchors):
        stop = anchors[n + 1][0] if n + 1 < len(anchors) else end
        block = '\n'.join(lines[i:stop])
        name = token
        if token in FIELD_WRAPS:
            name, suffix = FIELD_WRAPS[token]
            if not re.search(rf'^(?:[A-Z]{{1,2}} )?{suffix}\b', block, re.M):
                raise ValueError(f'Unverified wrapped field name: {token}')
        limits = re.search(r'\[(\d+)-(\d+)\]', block)
        printed = re.match(r'^([A-Z]{1,2})\s+' + re.escape(token) + r'\b', lines[i])
        printed_position = None
        if printed:
            printed_position = 0
            for char in printed[1]:
                printed_position = printed_position * 26 + ord(char) - ord('A') + 1
        data_type = 'date' if 'Fecha DD/MM/AAAA' in block else 'text' if 'Cadena' in lines[i] or name in {'COD_INS', 'COD_CAR', 'NRO_DOC', 'CEL'} else 'integer'
        fields.append({'name': name, 'position': len(fields) + 1, 'type': data_type,
                       'minimum': int(limits[1]) if limits else None,
                       'maximum': int(limits[2]) if limits else None,
                       'printed_column': printed[1] if printed else None,
                       'printed_position': printed_position,
                       'manual_line': i + 1, 'manual_block': block,
                       'source_requirement': EXTERNAL.get(name, '')})
    if len(fields) != 172 or len({f['name'] for f in fields}) != 172:
        raise ValueError(f'Expected 172 unique fields, found {len(fields)}')
    if fields[0]['name'] != 'PROCESO' or fields[-1]['name'] != 'DIS_ES_15':
        raise ValueError('Unexpected schema boundaries')
    return fields


def current_bindings(report):
    q = report['questions']
    reference_questions = json.loads(ENUM_REFERENCE.read_text())['questions']
    bindings = {}
    def bind(field, question, sub='', values=None, consent=None):
        if question not in q:
            raise ValueError(f'Unknown question: {question}')
        if sub and sub != 'other' and not any(s['code'] == sub for s in q[question]['subquestions']):
            raise ValueError(f'Unknown subquestion: {question}[{sub}]')
        bindings[field] = {'question': question, 'column': f'{question}[{sub}]' if sub else question,
                           'subquestion': sub, 'values': values, 'consent': consent}
    def choices(field, question, offset=1, consent=None):
        labels = [a['label'] for a in reference_questions[question]['answers']]
        if field == 'TIEMPO_TRAS':
            _, source = audit.REFERENCE['raw_manual'](2027)
            labels = audit.REFERENCE['choices'](source['P38']['block'])
        values = {audit.norm(label): i for i,label in enumerate(labels, offset)}
        bind(field, question, values={a['code']: values[audit.norm(a['label'])] for a in q[question]['answers']}, consent=consent)
    for field, question, consent in [
        ('SIT_MIGR', 'G02Q02', 'migration'), ('GENERO', 'G01Q03', 'gender'),
        ('PPOO', 'G01Q75', 'ancestry'), ('DISCAP', 'G01Q82', 'disability'),
        ('DISCAP_REGIS', 'G01Q30', 'disability'), ('CAMBIO_CIUDAD', 'G01Q33', None),
        ('CUIDADOS', 'G01Q10', None), ('APOYO_CUID', 'G01Q90', None),
        ('TIPO_EST_ESC', 'G03Q28', None), ('MOD_EM', 'G03Q31', None),
        ('TIT_MTP', 'G01Q45', None), ('ARTICULA', 'G03Q46', None),
        ('RAZ_NO_ARTICULA', 'G03Q47', None), ('EXP_LAB', 'G03Q48', None),
        ('EST_PRE', 'G03Q51', None), ('EST_PRE_REL', 'G03Q55', None),
        ('RAP', 'G03Q56', None), ('CON_SAL', 'G06Q61', 'health'),
        ('ORI_SAL_TIPO', 'G06Q97', 'health'), ('BIE_PSC', 'G01Q62', 'psychological'),
        ('ORI_PSC', 'G01Q63', 'psychological'), ('NEE', 'G01Q64', 'nee')]:
        if field not in ['GENERO','CUIDADOS']:
            choices(field, question, consent=consent)
    # Institutional refusal is not the official "Other" gender category.
    gender_values = {'masculino':1,'femenino':2,'nobinario':3,'otro':4,'prefieronodecirlo':None}
    bind('GENERO','G01Q03',values={a['code']:gender_values[audit.norm(a['label'])] for a in q['G01Q03']['answers']},consent='gender')
    bindings['GENERO']['values']['-oth-'] = 4
    care_values = {'si':1,'no':2,'noninguna':2}
    bind('CUIDADOS','G01Q10',values={a['code']:care_values[audit.norm(a['label'])] for a in q['G01Q10']['answers']})
    bind('SEXO', 'G00Q02', values={a['code']: {'hombre': 'H', 'mujer': 'M', 'nobinario': 'X'}[audit.norm(a['label'])] for a in q['G00Q02']['answers']})
    bind('JEFE_HOGAR', 'G01Q18', values={'Y': 1, 'N': 2})
    bind('HOGAR_SOLO', 'G02Q76', values={'AO01': 1, 'AO02': 0})
    bind('SIT_LAB', 'G02Q20', values={'AO03': 2, 'AO04': 3, 'AO05': 4})
    bind('RAZ_NO_RAP', 'G03Q57', values={'AO04': 1, 'AO05': 2, 'AO02': 3, 'AO03': 4})
    for field, question in [('ANO_EGRESO', 'G03Q30'), ('CUIDADOS_CANT', 'G02Q88')]:
        bind(field, question)
    bind('ANO_EGRESO', 'G03Q30', values={a['code']: int(a['label']) if a['label'].isdigit() else None for a in q['G03Q30']['answers']})
    checkbox = {'HOGAR': ('G02Q08', ['PADRE','MADRE','HERM','PAREJA','MEN12','MAY12','FAM','OTROS']),
                'FIN': ('G01Q19', ['PRO','PADRES','OFAM','OPER','GRAT','BEC_EST','BEC_EXT','CAE','CRE','EMP']),
                'EST_PRE': ('G03Q54', ['FFAA','TPINC','TPCOM','UINC','UCOM','PGINC','PFCOM','CAPCOM','CER','OTRO'])}
    for prefix, (question, suffixes) in checkbox.items():
        subcodes = [f'SQ{i:03d}' for i in range(2, len(suffixes) + 2)]
        if prefix == 'EST_PRE':
            subcodes = ['SQ002','SQ003','SQ004','SQ005','SQ006','SQ007','SQ008','SQ010','SQ011','SQ012']
        for suffix, sub in zip(suffixes, subcodes):
            bind(f'{prefix}_{suffix}', question, sub, {'Y':1,'N':0,'1':1,'0':0})
    _, manual = audit.REFERENCE['raw_manual'](2027)
    for prefix, question, ref in [('RAZ_TP','G04Q37','P25'), ('RAZ_INT','G04Q39','P26'),
                                  ('RAZ_CAR','G01Q50','P27'), ('MEDIOS','G01Q41','P28')]:
        labels = audit.REFERENCE['choices'](manual[ref]['block'])
        for index, label in enumerate(labels, 1):
            matches = [s for s in q[question]['subquestions'] if audit.norm(s['text']) == audit.norm(label)]
            if len(matches) != 1:
                raise ValueError(f'{prefix}_{index}: no unique official label match')
            bind(f'{prefix}_{index}', question, matches[0]['code'], {'Y':1,'N':0,'1':1,'0':0})
    for index, sub in enumerate(q['G01Q65']['subquestions'], 1):
        bind(f'NEE_{index}', 'G01Q65', sub['code'], {'Y':1,'N':0,'1':1,'0':0}, 'nee')
    bind('NEE_8', 'G01Q65', 'other', consent='nee')
    for prefix, question, offset in [('MAT','G01Q55',1), ('MIN','G01Q84',0), ('REC','G01Q67',1)]:
        suffixes = ['FAC','CLARO','RAP','ATE'] if prefix == 'MAT' else ['BEC','CAL','BUS','FUT','FUAS'] if prefix == 'MIN' else list(range(1,12))
        for suffix, sub in zip(suffixes, q[question]['subquestions']):
            bind(f'{prefix}_{suffix}', question, sub['code'], {a['code']: i for i,a in enumerate(q[question]['answers'],offset)})
    for suffix, sub in [('FAM','SQ002'), ('PAR','SQ003'), ('AMI','SQ005'), ('COL','SQ006'), ('OTR','SQ007'), ('NIN','SQ008')]:
        bind(f'RED_APO_{suffix}', 'G01Q69', sub, {'Y':1,'N':0,'1':1,'0':0})
    bindings['RED_APO_FAM']['additional_column'] = 'G01Q69[SQ004]'
    bindings['RED_APO_FAM']['status'] = 'REQUIRES_POLICY_FOR_OTHER_RELATIVES'
    choices('TIEMPO_TRAS', 'G01Q70')
    for item in report['disposition_mapping'] + report['disability_mapping']:
        bind(item['pes_field'], item['question'], item['subquestion'], item['code_to_value'],
             'disability' if item['pes_field'].startswith('DISCAP_') else None)
    bindings['NAC'] = {'status':'EXTERNAL_CATALOG', 'source_requirement':'Nacionalidad UMAS y catalogo Anexo 2. Chile/Otra en LimeSurvey no identifica el pais extranjero.'}
    for field, question in [('PPOO_DEF','G01Q05'), ('ESP_MTP','G03Q33'), ('ESP_MTP_EPJA','G03Q44')]:
        bindings[field] = {'status':'EXTERNAL_CATALOG', 'question': question,
                           'source_requirement':'Convertir mediante catalogo oficial, no por posicion de las alternativas.'}
        if field == 'PPOO_DEF':
            bindings[field]['consent'] = 'ancestry'
    bindings['CONTACTO'] = {'status':'EXTERNAL_DECISION', 'question':'G01Q43',
                           'source_requirement':'Resolver correo institucional/personal al codigo oficial Correo electronico; Web/RRSS no tienen equivalencia oficial automatica.'}
    for field in ['NIVEL_EDU_PADRE', 'NIVEL_EDU_MADRE']:
        bindings[field] = {'status':'EXTERNAL_CATALOG', 'source_requirement':'Seleccionar rama G00Q12/G02Q15 por familia homoparental y convertir con Anexo 7.'}
    return bindings


def missing(value):
    return value is None or str(value).strip().lower() in audit.MISSING_VALUES


def validate_value(field, value):
    if missing(value):
        return None
    name = field['name']
    if field['type'] == 'date':
        date = datetime.strptime(str(value), '%d/%m/%Y')
        if date.year > 2027:
            raise ValueError('Future birth date')
        return date.strftime('%d/%m/%Y')
    if name == 'SEXO':
        if value not in ['H','M','X']:
            raise ValueError('Invalid sex code')
        return value
    if name == 'CEL' and not re.fullmatch(r'569\d{8}', str(value)):
        raise ValueError('Cellphone must have 11 digits starting 569')
    if name == 'COD_CAR' and not re.fullmatch(r'\d{25}', str(value)):
        raise ValueError('Expected complete 25-digit SIES career code')
    if name == 'COD_INS' and not re.fullmatch(r'\d{3}', str(value)):
        raise ValueError('Expected three-digit SIES institution code')
    if name == 'ANO_EGRESO' and not re.fullmatch(r'\d{4}', str(value)):
        raise ValueError('Expected an exact four-digit graduation year')
    if name == 'CORREO' and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', str(value)):
        raise ValueError('Invalid personal email')
    length = re.search(r'(\d+) caracteres', field['manual_block'])
    if field['type'] == 'text' and length and len(str(value)) > int(length[1]):
        raise ValueError('Text exceeds official field length')
    if field['type'] == 'integer':
        if not re.fullmatch(r'\d+', str(value)):
            raise ValueError('Expected integer code')
        value = int(value)
        if field['minimum'] is not None and not field['minimum'] <= value <= field['maximum']:
            raise ValueError('Value outside official range')
    return value


def cohort_eligible(record, period):
    cohort = record.get('cohort', {})
    if cohort.get('admission_year') != 2027 or cohort.get('admission_period') != period:
        return False
    if cohort.get('enrollment_year') != 2027 or cohort.get('enrollment_period') != period:
        return False
    return cohort.get('eligible_student') is True


def instrument_matches(record, report):
    return record.get('survey_id') == report['survey'] and record.get('instrument_year') == 2027


def household_count(raw):
    if raw.get('G02Q76') == 'AO01':
        return 1
    if raw.get('G02Q76') != 'AO02':
        return None
    total, selected = 1, 0
    for sub in ['SQ002','SQ003','SQ005']:
        if raw.get(f'G02Q08[{sub}]') in ['Y','1',1,True]:
            total += 1
            selected += 1
    for sub, question in [('SQ004','G02Q77'), ('SQ006','G01Q78'), ('SQ007','G01Q79'),
                          ('SQ008','G01Q80'), ('SQ009','G02Q81')]:
        if raw.get(f'G02Q08[{sub}]') in ['Y','1',1,True]:
            value = raw.get(question)
            if missing(value) or not str(value).isdigit() or int(value) < 1:
                return None
            total += int(value)
            selected += 1
    return min(total, 10) if selected else None


def transform_record(record, fields, bindings):
    raw, prepared, consents = record.get('responses', {}), record.get('prepared', {}), record.get('consents', {})
    names = {f['name'] for f in fields}
    if set(prepared) - names:
        raise ValueError('Prepared data contains fields outside the 2027 schema')
    output, issues = {}, []
    if record.get('global_consent') is not True:
        return None, [{'issue':'GLOBAL_CONSENT_NOT_GRANTED'}]
    # A negative observed transfer consent cannot be bypassed by prepared values.
    consents = dict(consents)
    for group, question in [('migration','G00Q91'), ('gender','G00Q92'), ('ancestry','G00Q93'),
                            ('disability','G00Q94'), ('health','G06Q96'), ('nee','G06Q98')]:
        if raw.get(question) == 'AO02':
            consents[group] = False
        elif raw.get(question) == 'AO01' and group not in consents:
            consents[group] = True
    for field in fields:
        name = field['name']
        binding = bindings.get(name, {})
        consent = binding.get('consent')
        if consent and consents.get(consent) is not True:
            output[name] = None
            continue
        value = prepared.get(name)
        if name == 'PROCESO':
            value = 2027
        elif name == 'HOGAR_CANT' and name not in prepared:
            value = household_count(raw)
        elif name not in prepared and binding.get('column'):
            source_value = raw.get(binding['column'])
            if binding.get('status'):
                issues.append({'field':name,'issue':binding['status']})
            elif missing(source_value):
                value = None
                if binding.get('values') == {'Y':1,'N':0,'1':1,'0':0}:
                    prefix = binding['question'] + '['
                    answered = any(k.startswith(prefix) and (v in ['Y','1',1,True]
                                   or k.endswith('[other]') and not missing(v)) for k,v in raw.items())
                    if answered:
                        value = 0
            elif binding.get('values') is not None:
                try:
                    value = audit.decode_response(source_value, binding['values'])
                except ValueError:
                    value = None
                    issues.append({'field':name,'issue':'UNRECOGNIZED_RESPONSE_CODE'})
            elif name == 'NEE_8':
                value = 1
            else:
                value = source_value
        if missing(value) and not consent and name != 'DEPTO_BLOCK':
            issues.append({'field':name,'issue':'MISSING_OR_UNRESOLVED_SOURCE'})
        if name in ['CUIDADOS_CANT','HOGAR_CANT'] and str(value).isdigit():
            value = min(int(value), 5 if name == 'CUIDADOS_CANT' else 10)
        try:
            output[name] = validate_value(field, value)
        except ValueError as error:
            output[name] = None
            issues.append({'field':name,'issue':'INVALID_VALUE','detail':str(error)})
    # Gate-dependent outputs must not be invented from absence of the detail.
    if 'SIT_LAB' not in prepared and output.get('SIT_LAB') is None and raw.get('G02Q95') in ['AO03','AO04']:
        output['SIT_LAB'] = 1
        issues = [i for i in issues if i.get('field') != 'SIT_LAB']
    for gate, expected, targets in [('CUIDADOS',1,['CUIDADOS_CANT','APOYO_CUID']),
                                   ('EST_PRE',1,[n for n in names if n.startswith('EST_PRE_')]),
                                   ('NEE',1,[f'NEE_{i}' for i in range(1,9)])]:
        if output.get(gate) is not None and output[gate] != expected:
            for target in targets:
                output[target] = None
            issues = [i for i in issues if i.get('field') not in targets]
    conditionals = [
        (output.get('MOD_EM') == 3, ['ESP_MTP']),
        (output.get('MOD_EM') == 4, ['ESP_MTP_EPJA']),
        (output.get('MOD_EM') in [3,4], ['TIT_MTP','ARTICULA']),
        (output.get('ARTICULA') == 2, ['RAZ_NO_ARTICULA']),
        (output.get('EXP_LAB') == 1 or output.get('EST_PRE_REL') in [3,4], ['RAP']),
        (output.get('RAP') == 2, ['RAZ_NO_RAP'])]
    for relevant, targets in conditionals:
        if not relevant:
            for target in targets:
                output[target] = None
            issues = [i for i in issues if i.get('field') not in targets]
    if output.get('TIPO_DOC') == 1 and output.get('NRO_DOC') is not None:
        if not re.fullmatch(r'\d{8}-[0-9K]', str(output['NRO_DOC'])):
            issues.append({'field':'NRO_DOC','issue':'INVALID_RUN_FORMAT'})
        else:
            body, dv = output['NRO_DOC'].split('-')
            residue = 11 - sum(int(digit) * (2 + index % 6) for index,digit in enumerate(reversed(body))) % 11
            expected_dv = '0' if residue == 11 else 'K' if residue == 10 else str(residue)
            if dv != expected_dv:
                issues.append({'field':'NRO_DOC','issue':'INVALID_RUN_CHECK_DIGIT'})
    elif output.get('TIPO_DOC') == 2 and output.get('NRO_DOC') is not None:
        if not re.fullmatch(r'[A-Za-z0-9]{1,20}', str(output['NRO_DOC'])):
            issues.append({'field':'NRO_DOC','issue':'INVALID_PASSPORT_FORMAT'})
    elif output.get('TIPO_DOC') == 3 and output.get('NRO_DOC') is not None:
        if not re.fullmatch(r'\d{9}', str(output['NRO_DOC'])):
            issues.append({'field':'NRO_DOC','issue':'INVALID_IPE_FORMAT'})
    for prefix in ['RAZ_TP_', 'RAZ_INT_', 'RAZ_CAR_']:
        if sum(output.get(n) == 1 for n in names if n.startswith(prefix)) > 3:
            issues.append({'field':prefix,'issue':'MORE_THAN_THREE_SELECTIONS'})
    if output.get('RED_APO_NIN') == 1 and any(output.get(n) == 1 for n in names if n.startswith('RED_APO_') and n != 'RED_APO_NIN'):
        issues.append({'field':'RED_APO_NIN','issue':'CONTRADICTORY_SUPPORT_SELECTIONS'})
    return output, issues


def write_schema_csv(records, fields, output, delimiter=','):
    assert_frozen_reference()
    assert_2027_output_path(output)
    assert_private_output_path(Path(output).parent)
    if Path(output).suffix.lower() != '.csv':
        raise ValueError('Draft output must be a CSV, not an arbitrary project file')
    names = [f['name'] for f in fields]
    if len(names) != 172 or any(set(row) != set(names) for row in records):
        raise ValueError('Every output row must contain exactly the 172 official fields')
    if delimiter not in [',',';']:
        raise ValueError('Unsupported delimiter')
    rows = [[row[name] if row[name] is not None else '' for name in names] for row in records]
    for row in rows:
        if any('\n' in str(v) or '\r' in str(v) for v in row):
            raise ValueError('Multiline values cannot be silently flattened')
    with Path(output).open('w',encoding='utf-8',newline='') as stream:
        writer = csv.writer(stream,delimiter=delimiter,lineterminator='\n')
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--records', help='JSON records with responses, prepared fields, explicit consents and global_consent')
    parser.add_argument('--period', type=int, choices=[1,2,3])
    args = parser.parse_args()
    frozen_reference = assert_frozen_reference()
    assert_2027_output_path(args.output_dir)
    if args.records:
        assert_private_output_path(args.output_dir)
    report = json.loads(Path(args.audit).read_text())
    fields, bindings = schema_from_manual(), current_bindings(report)
    output = Path(args.output_dir)
    output.mkdir(parents=True,exist_ok=True)
    spec = {'schema_version':2027,'field_count':172,'manual_sha256':hashlib.sha256(MANUAL.read_bytes()).hexdigest(),
            'process_id':'FCU_CARGA_PES_2027','frozen_2026_reference':frozen_reference,
            'enum_reference':{'path':str(ENUM_REFERENCE),'sha256':hashlib.sha256(ENUM_REFERENCE.read_bytes()).hexdigest()},
            'fields':fields,'bindings':bindings,'sources':report['sources'],
            'policy':'No positional reuse of the 195-column 2026 file. Catalogs and external sources require validated prepared values.',
            'printed_column_conflicts':[{'field':f['name'],'sequence_position':f['position'],
                 'printed_column':f['printed_column'],'printed_position':f['printed_position']}
                 for f in fields if f['printed_position'] is not None and f['printed_position'] != f['position']],
            'official_load_blocked_reason':'Validate final PES template/column-letter discrepancies, sources and catalogs before official load. Generated CSVs are drafts only.',
            'production_ready':False}
    (output/'ESPECIFICACION_PES_2027.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
    if not args.records:
        print(json.dumps({'schema_fields':172,'bound_fields':len(bindings),'external_metadata_fields':len(EXTERNAL),'production_ready':False}))
        return
    if args.period is None:
        parser.error('--period is required for record export')
    records = json.loads(Path(args.records).read_text())
    run_id = hashlib.sha256(Path(args.records).read_bytes()).hexdigest()[:12]
    resolved, qa = [], []
    for index, record in enumerate(records):
        if not instrument_matches(record, report):
            qa.append({'record_index':index,'issue':'INSTRUMENT_VERSION_NOT_VERIFIED'})
            continue
        if not cohort_eligible(record, args.period):
            qa.append({'record_index':index,'issue':'COHORT_OUTSIDE_OR_NOT_VERIFIED'})
            continue
        row, issues = transform_record(record,fields,bindings)
        if row is not None:
            resolved.append(row)
        qa.extend({'record_index':index,**issue} for issue in issues)
    keys = [(r.get('COD_INS'),r.get('TIPO_DOC'),r.get('NRO_DOC')) for r in resolved]
    if len(set(keys)) != len(keys):
        qa.append({'issue':'DUPLICATE_INSTITUTION_DOCUMENT_KEY'})
    (output/f'QA_PES_2027_{run_id}.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
    if qa or not resolved:
        print(json.dumps({'draft_csv_written':False,'official_csv_written':False,'qa_issues':len(qa),'resolved_records':len(resolved)}))
        return
    write_schema_csv(resolved,fields,output/f'FCU_2027_BORRADOR_{run_id}.csv')
    print(json.dumps({'draft_csv_written':True,'official_csv_written':False,'records':len(resolved),'columns':172,'production_ready':False}))


if __name__ == '__main__':
    main()
