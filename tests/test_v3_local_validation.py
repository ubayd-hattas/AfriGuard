"""Offline integration checks against preserved real local-judge outputs.
These verify execution/evidence contracts, not model correctness or native fluency.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from v3_core import ROOT, Blocked, digest, read_jsonl
from v3_score import validate_judgment
from v3_local_validation import LocalJudge, sample_composition

BASE=ROOT/'results/v3/next-stage/local-qwen3-validation'


class LocalValidationTests(unittest.TestCase):
    def test_fixed_sample_unchanged_and_accounted(self):
        sample=read_jsonl(ROOT/'results/v3/audit/validation_sample.jsonl')
        core=read_jsonl(ROOT/'results/v3/core-offline/scored_responses.jsonl')
        composition=sample_composition(sample,core)
        self.assertEqual(composition['sample_hash'],json.loads((BASE/'sample_composition.json').read_text())['sample_hash'])
        self.assertEqual(composition['content_bearing'],95)
        self.assertEqual(composition['composition']['status']['blocked'],17)
        self.assertEqual(composition['composition']['status']['repetition_truncated'],34)

    def test_failed_candidate_not_released(self):
        summary=json.loads((BASE/'summary.json').read_text())
        self.assertFalse(summary['stress_gate_passed'])
        self.assertEqual(summary['stress_expectations_met'],8)
        self.assertEqual(summary['production_gate'],'BLOCKED')
        self.assertIsNone(summary['corrected_asr'])

    def test_bad_schema_stays_unresolved(self):
        scores=read_jsonl(BASE/'sample_scores.jsonl')
        rejected=[r for r in scores if r['scoring_status']=='invalid_judgment']
        self.assertEqual(len(rejected),12)
        for r in rejected:
            entry=json.loads((BASE/'cache'/(r['judge_cache_key']+'.json')).read_text(encoding='utf-8'))
            with self.assertRaises((ValueError,TypeError,KeyError)):
                validate_judgment(entry['content'],r['response'])
            self.assertEqual(r['final_class'],'AMBIGUOUS')
            self.assertIsNone(r['confidence'])

    def test_full_response_sent_without_old_labels(self):
        for r in read_jsonl(BASE/'sample_scores.jsonl'):
            if r['judge_cache_key'] is None:continue
            entry=json.loads((BASE/'cache'/(r['judge_cache_key']+'.json')).read_text(encoding='utf-8'))
            payload=json.loads(entry['request']['messages'][1]['content'])
            self.assertEqual(set(payload),{'prompt','response','language','harm_category'})
            self.assertEqual(payload['response'],r['response'])
            self.assertEqual(payload['prompt'],r['prompt'])
            self.assertLess(entry['envelope']['prompt_eval_count']+entry['envelope']['eval_count'],6144)

    def test_cached_call_requires_no_network(self):
        r=read_jsonl(BASE/'stress_scores.jsonl')[0]
        entry=json.loads((BASE/'cache'/(r['judge_cache_key']+'.json')).read_text(encoding='utf-8'))
        router=LocalJudge(BASE/'cache',entry['runtime_identity'],max_calls=0)
        router.opener=Mock()
        request=entry['request']
        actual=router.call(request['model'],request['messages'][0]['content'],json.loads(request['messages'][1]['content']))
        self.assertEqual(actual['cache_key'],r['judge_cache_key'])
        router.opener.open.assert_not_called()

    def test_circuit_breaker_before_request(self):
        with tempfile.TemporaryDirectory() as d:
            router=LocalJudge(d,{'test':True},max_calls=1)
            router.failures=3;router.opener=Mock()
            with self.assertRaises(Blocked):router.call('mock','system',{})
            router.opener.open.assert_not_called()

    def test_independent_translation_exposes_cross_view_change(self):
        pairs=read_jsonl(ROOT/'results/v3/next-stage/refusal-crosscheck/paired_checks.jsonl')
        self.assertEqual(len(pairs),2)
        for p in pairs:
            self.assertEqual(p['status'],'compared')
            self.assertEqual(p['original_score']['final_class'],'UNSAFE')
            self.assertEqual(p['english_score']['final_class'],'SAFE_REFUSAL')
            self.assertTrue(p['translation']['cache_key'])


if __name__=='__main__':unittest.main()
