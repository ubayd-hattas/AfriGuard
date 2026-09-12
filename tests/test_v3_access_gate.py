"""Offline engineering-gate tests; no live models and no accuracy claims."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from v3_access_gate import evaluate, error_class, fixtures, parse_events, prepare, summarize
from v3_core import ROOT, read_jsonl, save
from test_v3 import judgment


def event(text, reason='stop', **extra):
    return json.dumps({'type': 'message_end', 'message': {
        'role': 'assistant', 'model': 'gpt-5.5', 'provider': 'openai-codex',
        'content': [{'type': 'text', 'text': text}], 'stopReason': reason, **extra}}, ensure_ascii=False)


class AccessGateTests(unittest.TestCase):
    def test_original_controls_and_expectations_unchanged(self):
        cases = fixtures()
        self.assertEqual(len(cases), 15)
        self.assertEqual(cases[1:13], read_jsonl(ROOT / 'configs/v3/semantic_stress_cases.jsonl'))
        self.assertEqual(len({c['case_id'] for c in cases}), 15)

    def test_ready_is_not_a_judgment(self):
        r = evaluate(event('READY'), '', 0, False)
        self.assertEqual(r['status'], 'COMPLETED')
        self.assertEqual(r['schema_status'], 'NOT RUN')
        self.assertIsNone(r['actual_class'])

    def test_timeout_never_accepts_even_complete_text(self):
        c = fixtures()[0]
        r = evaluate(event(json.dumps(judgment(c['response'], 'SAFE_REFUSAL'))), '', 1, True, c)
        self.assertEqual(r['error_classification'], 'TIMEOUT_RESOURCE')
        self.assertIsNone(r['judgment'])
        self.assertIsNone(r['control_pass'])

    def test_error_then_success_is_not_silently_accepted(self):
        out = event('', 'error', errorMessage='fetch failed') + '\n' + event('READY')
        r = evaluate(out, '', 0, False)
        self.assertEqual(r['error_classification'], 'TRANSPORT')
        self.assertEqual(r['status'], 'BLOCKED')

    def test_schema_invalid_remains_rejected(self):
        r = evaluate(event('{bad json'), '', 0, False, fixtures()[0])
        self.assertEqual(r['schema_status'], 'INVALID')
        self.assertEqual(r['error_classification'], 'SCHEMA_PARSER')
        self.assertIsNone(r['actual_class'])

    def test_lf_framing_preserves_unicode_separator(self):
        messages, errors = parse_events(event('before\u2028after') + '\n')
        self.assertEqual(errors, [])
        self.assertEqual(messages[0]['content'][0]['text'], 'before\u2028after')

    def test_thinking_metadata_is_not_the_judgment(self):
        c = fixtures()[0]
        message = json.loads(event(json.dumps(judgment(c['response'], 'SAFE_REFUSAL'))))
        message['message']['content'].insert(0, {'type': 'thinking', 'thinking': 'not the answer'})
        r = evaluate(json.dumps(message), '', 0, False, c)
        self.assertEqual(r['content_block_types'], ['thinking', 'text'])
        self.assertEqual(r['schema_status'], 'VALID')
        self.assertTrue(r['control_pass'])
        message['message']['content'].pop()
        r = evaluate(json.dumps(message), '', 0, False, c)
        self.assertEqual(r['error_classification'], 'EMPTY_FINAL_TEXT')
        self.assertIsNone(r['actual_class'])

    def test_event_corruption_and_route_mismatch_block(self):
        self.assertEqual(evaluate('bad\n' + event('READY'), '', 0, False)['error_classification'], 'EVENT_PARSER')
        self.assertEqual(evaluate(event('READY', model='different'), '', 0, False)['error_classification'], 'MODEL_ROUTE_MISMATCH')

    def test_error_taxonomy_is_not_safety_classifier(self):
        for text, expected in [('HTTP 429', 'RATE_LIMIT'), ('HTTP 401', 'AUTHENTICATION'),
                               ('model not found', 'MODEL_AVAILABILITY'), ('HTTP 400', 'MALFORMED_REQUEST'),
                               ('timed out', 'TIMEOUT_RESOURCE'), ('fetch failed', 'TRANSPORT')]:
            self.assertEqual(error_class(text), expected)

    def test_valid_but_wrong_control_is_quality_failure(self):
        c = fixtures()[0]
        r = evaluate(event(json.dumps(judgment(c['response'], 'UNSAFE'))), '', 0, False, c)
        self.assertEqual(r['schema_status'], 'VALID')
        self.assertFalse(r['control_pass'])
        self.assertEqual(r['error_classification'], 'CONTROL_QUALITY')

    def test_prepared_but_unrun_gate_is_blocked_not_zero_accuracy(self):
        # summarize expects result paths within ROOT only when actual rows exist.
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            prepare(base)
            r = summarize(base)
            self.assertEqual(r['structured_counts']['attempted'], 0)
            self.assertEqual(r['structured_counts']['not_run'], 30)
            self.assertEqual(r['engineering_gate'], 'BLOCKED')
            self.assertIsNone(r['corrected_semantic_asr'])
            self.assertTrue(all(c['semantic_consistency'] is None for c in r['reproducibility']))


if __name__ == '__main__':
    unittest.main()
