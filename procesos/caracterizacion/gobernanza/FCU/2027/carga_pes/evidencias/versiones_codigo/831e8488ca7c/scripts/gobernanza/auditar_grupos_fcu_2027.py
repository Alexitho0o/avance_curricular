"""Read-only audit of the seven current LSG groups against FCU 2027."""
from pathlib import Path
from collections import Counter
import hashlib
import html
import json
import re
import runpy
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'gobernanza/FCU/2027/preparacion'
REVIEW_POLICY = BASE / 'json/POLITICA_REVISION_FCU_2027.json'
USER_CONFIRMATIONS = BASE / 'json/CONFIRMACIONES_USUARIO_FCU_2027.json'
REFERENCE = runpy.run_path(str(ROOT/'scripts/gobernanza/preparar_guia_fcu_2027.py'),run_name='reference_only')
norm = REFERENCE['norm']

def clean(value):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',value or ''))).strip()

def rows(root,table):
    return [{c.tag:c.text or '' for c in row} for row in root.findall(f'./{table}/rows/row')]


def read_current_groups(directory):
    questions, groups, conditions, sources = {}, [], [], []
    for gid in range(643, 650):
        paths = sorted(Path(directory).glob(f'limesurvey_group_{gid}_*.lsg'))
        if len(paths) != 1:
            raise ValueError(f'Group {gid}: expected one export, found {len(paths)}')
        path = paths[0]
        root = ET.parse(path).getroot()
        if root.findtext('./groups/rows/row/sid') != '141234':
            raise ValueError(f'Unexpected survey in {path}')
        texts = {q['qid']: clean(q['question']) for q in rows(root, 'question_l10ns')}
        labels = {a['aid']: clean(a['answer']) for a in rows(root, 'answer_l10ns')}
        parents, children = rows(root, 'questions'), rows(root, 'subquestions')
        answers, attributes = rows(root, 'answers'), rows(root, 'question_attributes')
        group = root.findtext('./group_l10ns/rows/row/group_name')
        groups.append({'gid': gid, 'group': group, 'questions': len(parents), 'subquestions': len(children)})
        for q in parents:
            code = q['title']
            if code in questions:
                raise ValueError(f'Duplicate question code: {code}')
            q.update(text=texts[q['qid']], group=group, gid=gid)
            q['subquestions'] = sorted([
                {'code': s['title'], 'text': texts[s['qid']], 'qid': s['qid'],
                 'order': int(s['question_order']), 'relevance': s.get('relevance', '')}
                for s in children if s['parent_qid'] == q['qid']
            ], key=lambda s: s['order'])
            q['answers'] = sorted([
                {'code': a['code'], 'label': labels[a['aid']], 'order': int(a['sortorder'])}
                for a in answers if a['qid'] == q['qid']
            ], key=lambda a: a['order'])
            q['attributes'] = {a['attribute']: a['value'] for a in attributes if a['qid'] == q['qid']}
            questions[code] = q
        conditions.extend(rows(root, 'conditions'))
        sources.append({'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return questions, groups, conditions, sources


def question_origins():
    official = set(REFERENCE['OFFICIAL']) | REFERENCE['CONSENTS'] | {'G01Q13', 'G02Q88', 'G06Q96', 'G06Q98'}
    institutional = (REFERENCE['INSTITUTIONAL'] - {'G01Q13'}) | {
        'G01Q15', 'G02Q77', 'G01Q78', 'G01Q79', 'G01Q80', 'G02Q81', 'G03Q32',
        'G03Q50', 'G03Q99', 'G03Q100', 'G01Q85', 'G06Q91', 'G06Q90'
    }
    if official & institutional:
        raise ValueError('Contradictory origin classification')
    return {**dict.fromkeys(official, 'FCU'), **dict.fromkeys(institutional, 'INSTITUCIONAL')}


def disposition_mapping(questions):
    expected = REFERENCE['NEW_DISPOSITION']
    candidates = [(code, s) for code, q in questions.items() if q['gid'] == 649
                  for s in q['subquestions']]
    result = []
    for index, text in enumerate(expected, 1):
        matches = [(code, s) for code, s in candidates if norm(s['text']) == norm(text)]
        if len(matches) != 1:
            raise ValueError(f'DIS_ES_{index}: expected one literal match, found {len(matches)}')
        code, sub = matches[0]
        labels = ['Muy en desacuerdo', 'En desacuerdo', 'De acuerdo', 'Muy de acuerdo']
        answers = questions[code]['answers']
        if questions[code]['type'] != 'F' or [norm(a['label']) for a in answers] != list(map(norm, labels)):
            raise ValueError(f'{code}: invalid four-point scale')
        result.append({'pes_field': f'DIS_ES_{index}', 'manual_id': f'DIS2027.{index}',
                       'question': code, 'subquestion': sub['code'],
                       'column': f"{code}[{sub['code']}]", 'text': text,
                       'group': questions[code]['group'],
                       'code_to_value': {a['code']: n for n, a in enumerate(answers, 1)}})
    return result


MISSING_VALUES = {'', 'na', 'n/a', 'nan', 'null', 'none', '-', '--', '.', 's/i', 'sin info'}


def decode_response(value, mapping, consent=True):
    if not consent or value is None or str(value).strip().lower() in MISSING_VALUES:
        return None
    key = str(value).strip()
    if key not in mapping:
        raise ValueError(f'Unknown response code: {key}')
    return mapping[key]


def disability_mapping(questions):
    question = questions['G01Q17']
    if question['type'] != 'F':
        raise ValueError('Disability mapping requires the observed severity matrix')
    severities = {norm('Leve'): 1, norm('Moderada'): 1, norm('Severa'): 1,
                  norm('No presento esta discapacidad'): 0}
    values = {a['code']: severities[norm(a['label'])] for a in question['answers']}
    accepted = [a['code'] for a in questions['G00Q94']['answers'] if norm(a['label']) == 'si']
    if len(accepted) != 1 or len(values) != 4:
        raise ValueError('Unexpected severity or consent alternatives')
    result = []
    for field, label in [('DISCAP_FIS', 'Sí, discapacidad física o motora'),
                         ('DISCAP_AUD', 'Sí, discapacidad auditiva'),
                         ('DISCAP_VIS', 'Sí, discapacidad visual'),
                         ('DISCAP_INT', 'Sí, discapacidad intelectual'),
                         ('DISCAP_PSQ', 'Sí, discapacidad psíquica')]:
        found = [s for s in question['subquestions'] if norm(s['text']).startswith(norm(label))]
        if len(found) != 1:
            raise ValueError(f'{field}: ambiguous disability item')
        sub = found[0]
        result.append({'pes_field': field, 'question': 'G01Q17', 'subquestion': sub['code'],
                       'column': f"G01Q17[{sub['code']}]", 'text': sub['text'],
                       'code_to_value': values, 'transfer_consent_question': 'G00Q94',
                       'transfer_consent_accepted_codes': accepted,
                       'missing_or_denied': None, 'unknown_response': 'error',
                       'original_severity_preserved': True,
                       'gate_no_policy': 'Not implemented. Do not infer transfer consent from a missing answer.'})
    return result


def partition_review_checks(checks, policy):
    allowed_ids = {'mandatory_setting', 'explicit_always_relevance'}
    rules = policy['excluded_recommendations']
    if any(r['check_id'] not in allowed_ids for r in rules):
        raise ValueError('Unsupported review exclusion: functional checks must remain active')
    active, excluded = [], []
    for check in checks:
        if not check.get('check_id'):
            check = {**check, 'check_id': {'Obligatoria': 'mandatory_setting',
                     'Relevancia explicita': 'explicit_always_relevance'}.get(check.get('setting'), check.get('setting'))}
        rule = next((r for r in rules if r['check_id'] == check.get('check_id')
                     and ('observed_values' not in r or check['observed'] in r['observed_values'])), None)
        if rule:
            excluded.append({**check, 'review_status': 'EXCLUIDO_POR_DECISION_USUARIO',
                             'exclusion_reason': rule['reason'], 'policy_version': policy['version']})
        else:
            active.append(check)
    return active, excluded


def apply_user_confirmations(checks, questions):
    confirmations = json.loads(USER_CONFIRMATIONS.read_text())['confirmations']
    result = []
    for check in checks:
        check = {k:v for k,v in check.items() if k not in {'confirmed_by_user','confirmation'}}
        matching = [c for c in confirmations if c.get('confirmed') is True
                    and c['code'] == check['code'] and c['check_id'] == check['check_id']
                    and c['expected'] == check['expected']]
        if matching:
            c = matching[0]
            subs = questions[check['code']]['subquestions']
            if any(s['code'] == c['expected'] and norm(s['text']) == norm(c['subquestion_text']) for s in subs):
                check = {**check, 'confirmed_by_user': True, 'confirmation': c}
        result.append(check)
    return result


def effective_ok(check):
    return check['ok'] or check.get('confirmed_by_user') is True


def main(destination, directory='/Users/alexi/Downloads'):
    questions, groups, conditions, sources = read_current_groups(directory)
    origins = question_origins()
    for code, q in questions.items():
        if code not in origins:
            raise ValueError(f'New code requires explicit origin evidence: {code}')
        q['origin'] = origins[code]
    checks = []
    def check(code, setting, observed, expected, check_id=None):
        checks.append({'code': code, 'group': questions[code]['group'], 'setting': setting,
                       'check_id': check_id or setting,
                       'observed': observed, 'expected': expected, 'ok': observed == expected})
    sensitive = ['G02Q02', 'G01Q03', 'G01Q75', 'G01Q05', 'G01Q82', 'G01Q17', 'G01Q30',
                 'G06Q61', 'G01Q62', 'G01Q64', 'G01Q65', 'G06Q90']
    for code in sensitive:
        check(code, 'Obligatoria', questions[code]['mandatory'], 'N', 'mandatory_setting')
    check('G01Q69', 'Opcion exclusiva', questions['G01Q69']['attributes'].get('exclude_all_others', ''), 'SQ008')
    for code in ['G01Q69', 'G01Q84']:
        check(code, 'Relevancia explicita', questions[code]['relevance'].strip(), '1', 'explicit_always_relevance')
    for code, label in [('AO04', 'Entre más de una hora y una hora y media'), ('AO05', 'Más de una hora y media')]:
        observed = next(a['label'] for a in questions['G01Q70']['answers'] if a['code'] == code)
        check('G01Q70', f'Texto {code}', observed, label)
    rubro = questions['G01Q26']['relevance']
    rubro_normalized = re.sub(r'[\s()]', '', rubro).replace("'", '"')
    rubro_ok = rubro_normalized in {
        'G02Q95.NAOK=="AO01"orG02Q95.NAOK=="AO02"',
        'G02Q95.NAOK=="AO02"orG02Q95.NAOK=="AO01"'
    }
    check('G01Q26', 'Condicion trabajo vigente', rubro_ok, True)
    mapping = disposition_mapping(questions)
    ids = {q['qid'] for q in questions.values()} | {s['qid'] for q in questions.values() for s in q['subquestions']}
    orphan_conditions = [c for c in conditions if any(c.get(k) and c[k] not in ids for k in ['qid', 'cqid'])]
    orphan_refs = [(code, ref) for code, q in questions.items()
                   for ref in re.findall(r'\bG\d+Q\d+\b', q['relevance']) if ref not in questions]
    duplicates = [code for code, q in questions.items()
                  if len({s['code'] for s in q['subquestions']}) != len(q['subquestions'])]
    blocks = [q for q in questions.values() if q['gid'] == 649 and q['subquestions']]
    block_order_ok = len(blocks) == 2 and sorted(len(q['subquestions']) for q in blocks) == [7, 8]
    for q in blocks:
        expected = REFERENCE['NEW_DISPOSITION'][:8] if len(q['subquestions']) == 8 else REFERENCE['NEW_DISPOSITION'][8:]
        block_order_ok &= [norm(s['text']) for s in q['subquestions']] == list(map(norm, expected))
    policy = json.loads(REVIEW_POLICY.read_text())
    checks, excluded_checks = partition_review_checks(checks, policy)
    checks = apply_user_confirmations(checks, questions)
    result = {'date': '2026-10-07', 'survey': 141234, 'sources': sources, 'groups': groups,
              'questions': questions, 'origins': dict(Counter(q['origin'] for q in questions.values())),
              'current_question_count': len(questions),
              'current_subquestion_count': sum(len(q['subquestions']) for q in questions.values()),
              'checks': checks, 'pending_checks': [c for c in checks if not effective_ok(c)],
              'excluded_checks': excluded_checks,
              'review_policy': {'path': str(REVIEW_POLICY), 'version': policy['version'],
                                'sha256': hashlib.sha256(REVIEW_POLICY.read_bytes()).hexdigest()},
              'disposition_mapping': mapping, 'disability_mapping': disability_mapping(questions),
              'disposition_blocks_ok': bool(block_order_ok),
              'orphan_conditions': orphan_conditions, 'orphan_relevance': orphan_refs,
              'duplicate_subquestion_codes': duplicates,
              'checked_settings_ready': all(effective_ok(c) for c in checks) and bool(block_order_ok)
                  and not orphan_conditions and not orphan_refs and not duplicates,
              'pes_ready': False,
              'scope': 'Partial mapping: 15 disposition and 5 disability fields. Readiness refers only to active checks under the recorded user policy, not full manual compliance or a complete PES 172-field adapter. Global consent and gate-no policies require integration tests.'}
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['origins', 'current_question_count', 'current_subquestion_count',
          'disposition_blocks_ok', 'checked_settings_ready', 'pes_ready']}, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '/Users/alexi/Downloads')
