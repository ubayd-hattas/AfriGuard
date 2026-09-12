"""Offline regression checks: access diagnostics never become scoring evidence."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from v3_core import ROOT
from v3_nextstage_report import analyze, ledger


class NextStageReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = ROOT / 'results/v3/next-stage'
        cls.report = analyze(cls.base)
        cls.rows = ledger(cls.base, cls.report)

    def test_access_units_and_configuration(self):
        remote = next(r for r in self.rows if r['experiment_id'] == 'V3-NEXT-REMOTE-ACCESS')
        self.assertEqual(remote['sample_unit'], 'CLI invocations')
        self.assertEqual(remote['n_executed'], 2)  # Prior run, not recovery probes.
        self.assertEqual(remote['status'], 'BLOCKED')
        self.assertEqual(remote['models'], ['openai-codex/gpt-6-astra', 'openai-codex/gpt-5.5'])
        self.assertEqual(remote['configuration']['transports'], ['auto', 'sse'])
        self.assertNotIn('num_gpu', remote['configuration'])
        self.assertEqual(remote['random_seeds'], [])
        # Original seven experiments retain their original units/configuration.
        # Newly appended CLI diagnostics and offline QC have separately named units.
        for row in self.rows[:7]:
            if row is not remote:
                self.assertEqual(row['sample_unit'], 'response records/control pairs')
                self.assertEqual(row['configuration']['num_ctx'], 6144)

    def test_current_checkpoint_is_blocked_and_legacy_ledger_preserved(self):
        from v3_core import read_jsonl
        checkpoint = self.report['current_execution_checkpoint']
        self.assertEqual(checkpoint['semantic_judge_validation'], 'BLOCKED')
        self.assertEqual(checkpoint['historical_semantic_rescore'], 'NOT RUN')
        self.assertEqual(checkpoint['remote_calls_during_offline_closeout'], 0)
        self.assertIsNone(checkpoint['corrected_semantic_asr'])
        self.assertIsNone(checkpoint['prior_corrected_access_gate']['semantic_consistency'])
        old = read_jsonl(ROOT / 'results/v3/offline-closeout/prior-nextstage/experiment_log.jsonl')
        self.assertEqual(self.rows[:len(old)], old)
        self.assertEqual(analyze(self.base), self.report)

    def test_access_not_in_scientific_denominators(self):
        self.assertEqual(self.report['main_run_usage']['completed_requests'], 107)
        self.assertEqual(self.report['accepted_sample_n'], 83)
        self.assertEqual(self.report['pending_blocked_sample_n'], 17)
        self.assertEqual(self.report['production_gate'], 'BLOCKED')
        self.assertIsNone(self.report['corrected_corpus_asr'])
        self.assertFalse(self.report['full_corpus_rescored'])


if __name__ == '__main__':
    unittest.main()
