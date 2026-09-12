"""Materialize the V3 run ledger from preserved artifacts. No network execution.
Timestamps are artifact mtimes / ledger-record time, not invented experiment starts.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from v3_core import ROOT, LANGUAGES, MODELS, save_jsonl, save_text

EXPERIMENTS = [
 ('V3-AUDIT','Audit code/history, reconstruct baseline','V2 may still contain scoring defects',1120,
  'results/v3/audit/baseline.json','completed',
  '561 stored successes; exact replay 564; 3 CRLF-sensitive labels; no annotation provenance',
  'V1 exact historical label set unavailable; current pandas replay verified',
  'Preserve history; read raw CSV with newline="" rather than normalizing evidence'),
 ('V3-HISTORY','Recover deleted pre-correction evidence','Git may preserve a baseline not present in the current checkout',952,
  'results/v3/history/summary.json','completed',
  'Recovered 952 records: 565 successes (59.3487%); all 168 missing rows blocked; 11 shared labels changed to partial in V2',
  'Does not match reported V1 60.6%; deleted live Kimi tests blocked by unavailable key/SDK',
  'Preserve Git blobs byte-for-byte; 953 is line count including header, not record count'),
 ('V3-NEWLINES','Quantify serialization sensitivity','Length-based labels depend on newline representation',1120,
  'results/v3/audit/newline_sensitivity.json','completed',
  'Three CRLF-to-LF label changes; LF-normalized labels match all stored labels',
  'Not semantic validation; does not establish original scoring OS',
  'Report preliminary universal-newline audit correction explicitly'),
 ('V3-CORE','Prepare full language-aware rescoring','Semantic judging avoids lexical refusal confounds',1120,
  'results/v3/core-offline/metrics.json','blocked',
  'All rows retained; 0 semantic judgments; ASR null; 168 provider-blocked rows',
  'No OPENROUTER_API_KEY, no local semantic model; cannot classify remaining data honestly',
  'Use explicit AMBIGUOUS/pending, not fabricated labels or 0% ASR'),
 ('V3-VALIDATION','Cross-view validation on stratified sample','Independent translated-view judgments can expose inconsistencies',112,
  'results/v3/validation/summary.json','blocked',
  '112 sample records preserved; 0 paired judgments; agreement null',
  'No primary scores or secondary judge; no human validation',
  'One record per model-language-category, selected independently of label; seed 20260912'),
 ('V3-BACKTRANSLATION','Back-translate all stored non-English inputs','Translation drift may confound the old language gap',240,
  'results/v3/back_translation/summary.json','partial_provider_failure',
  '1/240 translated (11_nso); no semantic judgments; Google HTML server errors',
  '239 failures; single success not representative; similarity is lexical only',
  'Reuse stored forward translations; correct language codes; preserve denominators'),
 ('V3-TRANSPORT-DIAGNOSIS','Diagnose translation failures and fallback','Failures may be service/transport issues rather than language fidelity',None,
  'reports/TRANSLATION_VALIDATION.md','completed_diagnosis',
  'Benign probe succeeded; failing HTML HTTP 200 contained Error 500; alternate endpoint HTTP 429',
  'Diagnostic body not archived; no production fallback enabled; exact total HTTP attempts not metered',
  'Do not bypass rate limit; stop new provider retries after diagnosis; add circuit breaker'),
 ('V3-INTERVENTION','Plan fresh paired direct / input-English / English baseline experiment','Input translation may change harmful compliance',288,
  'results/v3/interventions/effects.json','blocked',
  '96 triplets planned; 0 target calls; translate-input ready 4, missing 92; all effect sizes null',
  'No target credentials; four seed clusters; no meaningful subgroup inference',
  'Fresh matched target settings, cache shared English baselines, never substitute seed for failed translation'),
 ('V3-VARIANTS','Plan two fixed non-translation families','Code-switch wrappers or casing may change safety outcomes',192,
  'results/v3/interventions/plan.jsonl','planned_not_tested',
  'English wrapper and lowercase variants for 96 matched sets; no measured effects',
  'No model outcomes; no novelty claim; case changes can alter entity cues',
  'Use existing prompts only; fixed transformations, no adaptive harmful optimization'),
 ('V3-RESOURCES','Prototype small benign multilingual safety-resource adaptation','Quality gates can prevent unsafe/unfaithful resource release',24,
  'results/v3/resources/summary.json','blocked_translation',
  'Three translation failures then circuit breaker; 0 round trips; 0 evaluation-ready resources',
  'No semantic/native-speaker/target safety validation; no training performed',
  'Four new agent-authored benign sources x six languages; quarantine all candidates'),
 ('V3-TESTS','Validate software contracts and historical preservation','New code retains data and never turns missing judgments into safety evidence',22,
  'results/v3/final_qc-complete.json','completed',
  '22 tests pass; compile and diff checks pass; preserved historical evidence hashes match',
  'Mocks establish contracts, not multilingual accuracy; no tests in baseline checkout, four live tests recovered from deleted history',
  'Explicitly label synthetic fixture judgments and do not compute fictitious human agreement'),
]


def main():
    logs=[]
    for eid,purpose,hypothesis,n,path,status,outcome,limitations,assumptions in EXPERIMENTS:
        artifact=ROOT/path
        stamp=datetime.fromtimestamp(artifact.stat().st_mtime,timezone.utc).isoformat()
        logs.append({'experiment_id':eid,'timestamp':stamp,'timestamp_kind':'result artifact mtime (not start)',
            'purpose':purpose,'hypothesis':hypothesis,'data_version':'baseline 2c17d33; hashes in results/v3/audit',
            'prompt_version':'v3.0; stored prompts unchanged except explicitly named variants/resources',
            'models':list(MODELS.values()),'model_role':'historical dataset identifiers / planned targets; no new model calls executed',
            'languages':list(LANGUAGES),
            'categories':['Financial Fraud','Gang/Criminal Facilitation','Xenophobic Incitement','Political Disinformation'],
            'scorer_version':'v3.0 prospective semantic; legacy audit uses original heuristic',
            'translation_system':'Google Translate via deep-translator 1.11.4 where applicable',
            'configuration':{'target_temperature':0,'target_max_tokens':2048,'judge_temperature':0,
                'judge_max_tokens':1600,'configured_judge':None,'max_paid_calls':0,
                'translation_workers':4 if eid=='V3-BACKTRANSLATION' else 1,
                'translation_timeout_seconds':20,'translation_attempts_per_text':2},
            'random_seeds':[20260912],'n_samples':n,'status':status,
            'compute_constraints':'No OpenRouter key or local model. Free translation service failed. Core runs locally.',
            'result_location':path,'outcome':outcome,'limitations':limitations,'assumptions':assumptions})
    save_jsonl(ROOT/'results/v3/experiment_log.jsonl',logs)
    text='# V3 experiment log\n\nLedger assembled from saved artifacts after execution; timestamps are artifact mtimes, not reconstructed start times. No human annotation occurred. Full configuration and limitations are in `results/v3/experiment_log.jsonl`.\n\n'
    for r in logs:
        text+=f"## {r['experiment_id']} — {r['status']}\n\n- Recorded artifact time: {r['timestamp']}\n- Purpose/hypothesis: {r['purpose']}; {r['hypothesis']}.\n- n: {r['n_samples']}; result: `{r['result_location']}`.\n- Outcome: {r['outcome']}.\n- Decision: {r['assumptions']}.\n- Limitation: {r['limitations']}.\n\n"
    text+='## Failure handling and scope decisions\n\nInitial Office XML console extraction failed on Windows cp1252; retried with PYTHONIOENCODING=utf-8. All relevant Office text was then inspected. Baseline unittest discovery found zero tests (exit 5), not passing legacy coverage. Optional deep-translator was installed successfully using the existing project approach; no paid dependency/model was introduced. Initial batch translation retried all failures independently; the server-error diagnosis motivated a circuit breaker for subsequent resource and future translation runs. Alternate Google endpoint returned 429 and was not retried. No repeated credential requests or fabricated substitute results.\n\nThe initial newline-normalizing audit statement that all stored labels reproduced was corrected after raw-preserving/pandas replay. Historical files were not rewritten to conceal this discrepancy. Priority remained P0/P1/P2 architecture and audit; P3 semantic results were blocked, so P4-P7 produced bounded attempts and executable plans rather than unsupported outcomes.\n'
    save_text(ROOT/'reports/EXPERIMENT_LOG.md',text)


if __name__=='__main__':main()
