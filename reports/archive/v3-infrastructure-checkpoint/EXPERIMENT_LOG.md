# V3 experiment log

Ledger assembled from saved artifacts after execution; timestamps are artifact mtimes, not reconstructed start times. No human annotation occurred. Full configuration and limitations are in `results/v3/experiment_log.jsonl`.

## V3-AUDIT — completed

- Recorded artifact time: 2026-09-12T08:58:32.999549+00:00
- Purpose/hypothesis: Audit code/history, reconstruct baseline; V2 may still contain scoring defects.
- n: 1120; result: `results/v3/audit/baseline.json`.
- Outcome: 561 stored successes; exact replay 564; 3 CRLF-sensitive labels; no annotation provenance.
- Decision: Preserve history; read raw CSV with newline="" rather than normalizing evidence.
- Limitation: V1 exact historical label set unavailable; current pandas replay verified.

## V3-HISTORY — completed

- Recorded artifact time: 2026-09-12T09:17:36.317847+00:00
- Purpose/hypothesis: Recover deleted pre-correction evidence; Git may preserve a baseline not present in the current checkout.
- n: 952; result: `results/v3/history/summary.json`.
- Outcome: Recovered 952 records: 565 successes (59.3487%); all 168 missing rows blocked; 11 shared labels changed to partial in V2.
- Decision: Preserve Git blobs byte-for-byte; 953 is line count including header, not record count.
- Limitation: Does not match reported V1 60.6%; deleted live Kimi tests blocked by unavailable key/SDK.

## V3-NEWLINES — completed

- Recorded artifact time: 2026-09-12T09:12:49.650810+00:00
- Purpose/hypothesis: Quantify serialization sensitivity; Length-based labels depend on newline representation.
- n: 1120; result: `results/v3/audit/newline_sensitivity.json`.
- Outcome: Three CRLF-to-LF label changes; LF-normalized labels match all stored labels.
- Decision: Report preliminary universal-newline audit correction explicitly.
- Limitation: Not semantic validation; does not establish original scoring OS.

## V3-CORE — blocked

- Recorded artifact time: 2026-09-12T08:58:33.665448+00:00
- Purpose/hypothesis: Prepare full language-aware rescoring; Semantic judging avoids lexical refusal confounds.
- n: 1120; result: `results/v3/core-offline/metrics.json`.
- Outcome: All rows retained; 0 semantic judgments; ASR null; 168 provider-blocked rows.
- Decision: Use explicit AMBIGUOUS/pending, not fabricated labels or 0% ASR.
- Limitation: No OPENROUTER_API_KEY, no local semantic model; cannot classify remaining data honestly.

## V3-VALIDATION — blocked

- Recorded artifact time: 2026-09-12T09:05:16.776095+00:00
- Purpose/hypothesis: Cross-view validation on stratified sample; Independent translated-view judgments can expose inconsistencies.
- n: 112; result: `results/v3/validation/summary.json`.
- Outcome: 112 sample records preserved; 0 paired judgments; agreement null.
- Decision: One record per model-language-category, selected independently of label; seed 20260912.
- Limitation: No primary scores or secondary judge; no human validation.

## V3-BACKTRANSLATION — partial_provider_failure

- Recorded artifact time: 2026-09-12T09:02:28.294019+00:00
- Purpose/hypothesis: Back-translate all stored non-English inputs; Translation drift may confound the old language gap.
- n: 240; result: `results/v3/back_translation/summary.json`.
- Outcome: 1/240 translated (11_nso); no semantic judgments; Google HTML server errors.
- Decision: Reuse stored forward translations; correct language codes; preserve denominators.
- Limitation: 239 failures; single success not representative; similarity is lexical only.

## V3-TRANSPORT-DIAGNOSIS — completed_diagnosis

- Recorded artifact time: 2026-09-12T09:18:36.469334+00:00
- Purpose/hypothesis: Diagnose translation failures and fallback; Failures may be service/transport issues rather than language fidelity.
- n: None; result: `reports/TRANSLATION_VALIDATION.md`.
- Outcome: Benign probe succeeded; failing HTML HTTP 200 contained Error 500; alternate endpoint HTTP 429.
- Decision: Do not bypass rate limit; stop new provider retries after diagnosis; add circuit breaker.
- Limitation: Diagnostic body not archived; no production fallback enabled; exact total HTTP attempts not metered.

## V3-INTERVENTION — blocked

- Recorded artifact time: 2026-09-12T09:05:09.529563+00:00
- Purpose/hypothesis: Plan fresh paired direct / input-English / English baseline experiment; Input translation may change harmful compliance.
- n: 288; result: `results/v3/interventions/effects.json`.
- Outcome: 96 triplets planned; 0 target calls; translate-input ready 4, missing 92; all effect sizes null.
- Decision: Fresh matched target settings, cache shared English baselines, never substitute seed for failed translation.
- Limitation: No target credentials; four seed clusters; no meaningful subgroup inference.

## V3-VARIANTS — planned_not_tested

- Recorded artifact time: 2026-09-12T09:05:09.487417+00:00
- Purpose/hypothesis: Plan two fixed non-translation families; Code-switch wrappers or casing may change safety outcomes.
- n: 192; result: `results/v3/interventions/plan.jsonl`.
- Outcome: English wrapper and lowercase variants for 96 matched sets; no measured effects.
- Decision: Use existing prompts only; fixed transformations, no adaptive harmful optimization.
- Limitation: No model outcomes; no novelty claim; case changes can alter entity cues.

## V3-RESOURCES — blocked_translation

- Recorded artifact time: 2026-09-12T09:05:16.240671+00:00
- Purpose/hypothesis: Prototype small benign multilingual safety-resource adaptation; Quality gates can prevent unsafe/unfaithful resource release.
- n: 24; result: `results/v3/resources/summary.json`.
- Outcome: Three translation failures then circuit breaker; 0 round trips; 0 evaluation-ready resources.
- Decision: Four new agent-authored benign sources x six languages; quarantine all candidates.
- Limitation: No semantic/native-speaker/target safety validation; no training performed.

## V3-TESTS — completed

- Recorded artifact time: 2026-09-12T09:20:46.369961+00:00
- Purpose/hypothesis: Validate software contracts and historical preservation; New code retains data and never turns missing judgments into safety evidence.
- n: 22; result: `results/v3/final_qc-complete.json`.
- Outcome: 22 tests pass; compile and diff checks pass; preserved historical evidence hashes match.
- Decision: Explicitly label synthetic fixture judgments and do not compute fictitious human agreement.
- Limitation: Mocks establish contracts, not multilingual accuracy; no tests in baseline checkout, four live tests recovered from deleted history.

## Failure handling and scope decisions

Initial Office XML console extraction failed on Windows cp1252; retried with PYTHONIOENCODING=utf-8. All relevant Office text was then inspected. Baseline unittest discovery found zero tests (exit 5), not passing legacy coverage. Optional deep-translator was installed successfully using the existing project approach; no paid dependency/model was introduced. Initial batch translation retried all failures independently; the server-error diagnosis motivated a circuit breaker for subsequent resource and future translation runs. Alternate Google endpoint returned 429 and was not retried. No repeated credential requests or fabricated substitute results.

The initial newline-normalizing audit statement that all stored labels reproduced was corrected after raw-preserving/pandas replay. Historical files were not rewritten to conceal this discrepancy. Priority remained P0/P1/P2 architecture and audit; P3 semantic results were blocked, so P4-P7 produced bounded attempts and executable plans rather than unsupported outcomes.
