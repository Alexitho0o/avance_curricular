import copy
import json
import unittest

import auditar_grupos_fcu_2027 as audit


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.questions = {}
        for code, texts in [('G07Q71', audit.REFERENCE['NEW_DISPOSITION'][:8]),
                            ('G01Q72', audit.REFERENCE['NEW_DISPOSITION'][8:])]:
            self.questions[code] = {
                'gid': 649, 'group': 'DISPOSICION', 'type': 'F',
                'answers': [{'code': f'AO0{i}', 'label': label} for i, label in enumerate(
                    ['Muy en desacuerdo', 'En desacuerdo', 'De acuerdo', 'Muy de acuerdo'], 1)],
                'subquestions': [{'code': f'SQ{i:03d}', 'text': text} for i, text in enumerate(texts, 4)]}

    def test_all_fifteen_literal_links(self):
        result = audit.disposition_mapping(self.questions)
        self.assertEqual([r['pes_field'] for r in result], [f'DIS_ES_{i}' for i in range(1, 16)])
        self.assertEqual(result[0]['column'], 'G07Q71[SQ004]')

    def test_renumbering_is_matched_by_text_not_position(self):
        self.questions['G07Q71']['subquestions'][0]['code'] = 'SQ900'
        self.questions['G07Q71']['subquestions'].reverse()
        self.assertEqual(audit.disposition_mapping(self.questions)[0]['column'], 'G07Q71[SQ900]')

    def test_duplicate_or_missing_text_fails(self):
        for duplicate in [True, False]:
            q = copy.deepcopy(self.questions)
            if duplicate:
                q['G01Q72']['subquestions'].append(q['G07Q71']['subquestions'][0])
            else:
                q['G07Q71']['subquestions'].pop(0)
            with self.assertRaises(ValueError):
                audit.disposition_mapping(q)

    def test_five_point_scale_fails(self):
        self.questions['G07Q71']['type'] = 'A'
        with self.assertRaises(ValueError):
            audit.disposition_mapping(self.questions)

    def test_decode_missing_denied_and_invalid(self):
        mapping = {'AO01': 1, 'AO02': 2, 'AO03': 3, 'AO04': 4}
        for key, expected in mapping.items():
            self.assertEqual(audit.decode_response(key, mapping), expected)
        for value in [None, '', '  ', 'nan', 'sin info']:
            self.assertIsNone(audit.decode_response(value, mapping))
        self.assertIsNone(audit.decode_response('AO03', mapping, consent=False))
        for value in ['AO05', '1', 0]:
            with self.assertRaises(ValueError):
                audit.decode_response(value, mapping)

    def test_origin_has_only_two_categories(self):
        origins = audit.question_origins()
        self.assertEqual(set(origins.values()), {'FCU', 'INSTITUCIONAL'})
        self.assertEqual(len(origins), 103)
        self.assertEqual(origins['G01Q13'], 'FCU')
        self.assertEqual(origins['G06Q90'], 'INSTITUCIONAL')

    def test_severity_mapping_preserves_missing_and_consent(self):
        q = {'G01Q17': {'type': 'F', 'answers': [
            {'code': 'S', 'label': 'Severa'}, {'code': 'L', 'label': 'Leve'},
            {'code': 'M', 'label': 'Moderada'}, {'code': 'NO', 'label': 'No presento esta discapacidad'}],
            'subquestions': [{'code': str(i), 'text': text} for i, text in enumerate([
                'Sí, discapacidad física o motora', 'Sí, discapacidad auditiva',
                'Sí, discapacidad visual', 'Sí, discapacidad intelectual', 'Sí, discapacidad psíquica'])]},
             'G00Q94': {'answers': [{'code': 'YES', 'label': 'Sí'}, {'code': 'NO', 'label': 'No'}]}}
        result = audit.disability_mapping(q)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]['code_to_value'], {'S': 1, 'L': 1, 'M': 1, 'NO': 0})
        self.assertEqual(result[0]['transfer_consent_accepted_codes'], ['YES'])
        self.assertIsNone(audit.decode_response(None, result[0]['code_to_value']))
        self.assertIsNone(audit.decode_response('S', result[0]['code_to_value'], consent=False))
        self.assertEqual(audit.decode_response('NO', result[0]['code_to_value']), 0)

    def test_user_policy_excludes_only_selected_recommendations(self):
        policy = json.loads(audit.REVIEW_POLICY.read_text())
        checks = [
            {'check_id': 'mandatory_setting', 'observed': 'Y', 'ok': False},
            {'check_id': 'explicit_always_relevance', 'observed': '', 'ok': False},
            {'check_id': 'explicit_always_relevance', 'observed': 'G06Q91 == "AO01"', 'ok': False},
            {'check_id': 'functional_filters', 'observed': False, 'ok': False},
            {'check_id': 'transfer_consent', 'observed': False, 'ok': False}]
        active, excluded = audit.partition_review_checks(checks, policy)
        self.assertEqual(len(excluded), 2)
        self.assertTrue(all(not c['ok'] for c in excluded))
        self.assertEqual(len(active), 3)
        self.assertIn('functional_filters', [c['check_id'] for c in active])
        self.assertIn('transfer_consent', [c['check_id'] for c in active])

    def test_policy_cannot_disable_functional_checks(self):
        with self.assertRaises(ValueError):
            audit.partition_review_checks([], {'excluded_recommendations': [{'check_id': 'transfer_consent'}]})

    def test_legacy_report_labels_also_follow_policy(self):
        policy = json.loads(audit.REVIEW_POLICY.read_text())
        active, excluded = audit.partition_review_checks([
            {'setting': 'Obligatoria', 'observed': 'Y', 'ok': False},
            {'setting': 'Relevancia explicita', 'observed': '', 'ok': False}], policy)
        self.assertEqual(active, [])
        self.assertEqual(len(excluded), 2)

    def test_user_confirmation_is_not_a_fabricated_xml_change(self):
        checks = [{'code':'G01Q69','check_id':'Opcion exclusiva','expected':'SQ008','observed':'','ok':False}]
        questions = {'G01Q69':{'subquestions':[{'code':'SQ008','text':'No cuento con red de apoyo'}]}}
        updated = audit.apply_user_confirmations(checks,questions)
        self.assertFalse(updated[0]['ok'])
        self.assertEqual(updated[0]['observed'],'')
        self.assertTrue(audit.effective_ok(updated[0]))
        questions['G01Q69']['subquestions'][0]['code'] = 'SQ099'
        self.assertFalse(audit.effective_ok(audit.apply_user_confirmations(checks,questions)[0]))
        self.assertFalse(audit.effective_ok(audit.apply_user_confirmations(updated,questions)[0]))


if __name__ == '__main__':
    unittest.main()
