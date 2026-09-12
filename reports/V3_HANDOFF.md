# AfriGuard V3 handoff

**Current gate:** neither judge is approved. The local Qwen3 8B candidate failed its stress gate (8/12 expectations; two African-language refusals mislabeled unsafe). The later remote gate returned one valid English control judgment, but the identical repeat and permitted WebSocket access-only probe failed at transport, so it is not reproducible. Full semantic rescoring was not run and corpus semantic ASR remains unavailable. See [JUDGE_GATE_BLOCKED.md](JUDGE_GATE_BLOCKED.md).

**Earlier recovery checkpoint:** offline reproduction succeeded. A CLI READY probe and one structured Afrikaans control succeeded, but the next control timed out at 45 seconds. No fixed-sample rerun, full rescore, translation batch or intervention was launched. See [V3_RECOVERY.md](V3_RECOVERY.md) and `results/v3/recovery/`; this earlier access finding is superseded by the current gate above.

**Latest outcome (2026-09-12 next stage): real semantic validation executed; candidate NOT approved; corrected corpus ASR remains BLOCKED.** Latest machine-readable summary: `results/v3/next-stage/final_summary.json`. Full account: [SEMANTIC_VALIDATION_NEXT_STAGE.md](SEMANTIC_VALIDATION_NEXT_STAGE.md).

### Next-stage handoff
- Found and tested existing Ollama Qwen3 8B Q4_K_M on the unchanged 112-record sample (95 content-bearing +17 blocked) and 12 separate synthetic controls. No new model download or raw API credential was required for this local run.
- Completed 107 main judge calls and two English-translation control judgments. Candidate sample outputs: 42 UNSAFE, 30 SAFE_REFUSAL, 11 SAFE_OTHER; 12 invalid judgments and 17 blocked records remain unresolved. These are **not validated corpus frequencies**; corrected ASR and true class-rate intervals remain null.
- Stress expectations met: 8/12. Two African-language refusals were labeled UNSAFE at 0.95 confidence. Independent Google translations confirmed refusal-like English meanings; the same judge labeled both English views SAFE_REFUSAL. **The production gate did not pass.**
- Existing CLI-managed OAuth access was tested, not ignored: automatic/SSE provider requests failed. Claude CLI is not authenticated. No functioning independent judge or native-speaker review was obtained.
- Full rescoring, 240-prompt translation retry, target interventions, novel-attack execution and resource release were deliberately NOT expanded. No zero-effect claim.
- Added `scripts/v3_local_validation.py`, `scripts/v3_nextstage_report.py`, `configs/v3/semantic_stress_cases.jsonl`, seven integration tests, detailed validation report and immutable `results/v3/next-stage/` artifacts. Existing V3 architecture/rubric/raw data/fixed sample remain intact. Prior versions of updated reports are archived under `reports/archive/v3-infrastructure-checkpoint/`.
- **29 tests pass.** Next action: obtain a reachable independent judge and language-validity review; rerun the fixed validation gate before any production scoring. Restore authorized provider connectivity or supply suitable provider access—not merely another unvalidated small local model.

The remainder records the **prior infrastructure-checkpoint handoff**. Its earlier absence-of-access statements are superseded by the next-stage evidence above. Original machine-readable snapshot remains `results/v3/final_summary.json`.

## A. Repository state
- Branch `main`, baseline commit `2c17d33`; no new commits or history rewrites.
- Modified: `README.md`, `analytics/dashboard.py` (prominent historical-method warning).
- Added: `scripts/v3_*.py`, frozen judge rubric, optional translation requirements, 22 contract tests, audits/methodology/results/limitations/claim corrections/logs, versioned V3 outputs, recovered deleted historical evidence and supersession notices.
- Preserved: all original data, V1/V2 reports/slides/table and legacy scoring code. Previous README copied verbatim to `reports/archive/README_V2_2c17d33.md`. Hash QC verifies preservation. User-supplied `new feedback/` remains untouched/untracked.
- Exact added/modified/preserved file inventory is in the JSON summary.

## B. Critical findings
V2 still uses English regex and length, with a constant `partial` LLM fallback. It can mark long gibberish/non-English refusals as compliance and harmful content containing refusal words as safe. The completeness correction also disabled live fallback judging.

Deleted history was recovered: **952 pre-correction records, not 953** (the latter counts the header). All 168 omitted records have blocked status; eleven shared labels also changed to partial. The older 200-row benchmark and separate Kimi judge/four live calibration cases are preserved for provenance, not presented as new validation.

Three current replay labels depend on CRLF versus LF crossing the 400-character threshold. New V3 scoring is full-text and semantic, with strict structured judgments, exact evidence checks, separate quality/safety classes, cached requests and explicit pending states. Its multilingual accuracy has not yet been validated.

## C. Results
| Baseline | ASR interpretation |
|---|---|
| V1 report | 60.6%; internally inconsistent |
| Recovered pre-correction CSV | 565/952 = 59.3487%, historical heuristic |
| V2 stored | 561/1,120 = 50.0893%, historical heuristic |
| Exact current legacy replay | 564/1,120 = 50.3571%, three newline artifacts |
| **V3 semantic** | **Unavailable; difference and relative difference null** |

319/561 old apparent successes are repetition-truncated (56.86%). This is not a measured gibberish/false-positive fraction. All V3 rows are retained pending; coverage 0%, bounds [0,1], not a 0% ASR. A stratified 112-record validation sample is prepared; zero paired validations/human annotations completed.

## D. Translation validation
Attempted 240 back-translations, one success (`11_nso`): Jaccard 0.7333, character similarity 0.9173. These are surface metrics, not semantic fidelity. The service returned error pages; alternate endpoint returned 429. No translation-drift estimate is defensible. Failures are preserved and future attempts have a circuit breaker.

## E. Intervention results
96 fresh matched triplets planned: direct African input, translated-English input, original English baseline. Zero target calls because credentials are unavailable; no effect or confidence interval. Only four translate-input tasks have a back-translation; 92 are blocked. Target-input translation is explicitly separate from translating outputs for judge validation.

## F. Non-translation families
English wrapper (inter-sentential code-switching) and lowercase orthographic variation: 192 fixed candidate tasks, no generated target outcomes. Four prespecified seeds; exploratory design only. No attack efficacy or novelty claim.

## G. Automated resource prototype
Four NEW agent-authored benign refusal/prevention resources ×six languages =24 candidates. Three initial translation failures triggered the circuit breaker; zero completed round trips. All candidates quarantined; none are evaluation/training-ready. No classifier training occurred.

## H. Scientific claims
- **Retained:** regional coverage, dataset availability, historical label arithmetic.
- **Weakened:** V2 corrected completeness only; safety gap/rankings require semantic validation.
- **Corrected:** 1,120 responses versus distinct prompts; disabled LLM fallback; monolingual metric mislabeled code-switching; 952 records versus 953 lines.
- **Withdrawn from current claims:** human scoring, kappa 0.82, native-speaker validation, first-discovery priority, causal morphology/MoE claims and validated catastrophic ASR.
- **Newly supported:** recovered historical omissions/transitions; newline sensitivity; quality-flag contingency; working auditable scoring contracts and 22 passing software tests.

## I. Limitations / QC
Missing judge/target access, missing original finish reasons, 168 provider-blocked records, translation-service failures, no human validation and no new target outcomes remain material blockers. Mock tests validate software, not language competence. Recovered historical live tests require unavailable Kimi credentials/SDK and were not claimed to run.

Final QC: 22 tests pass; all current source compiles; `git diff --check` passes; original evidence hashes and archived README match. No credentials were introduced. See `results/v3/final_qc-complete.json`, `results/v3/experiment_log.jsonl` and `reports/EXPERIMENT_LOG.md`.

## J. Next justified steps
1. Validate a multilingual judge on the fixed sample with qualified native speakers and independent translated-view checks.
2. Recover provider/collection/truncation logs; rescore 952 content-bearing responses and publish unresolved bounds for missing evidence.
3. Complete authorized translation and semantic fidelity validation, especially unresolved xh/st/nso provenance.
4. Run the fresh paired pilot before expanding categories, attack families or resource generation.

## Reviewer checklist
- [x] Feedback read; source/data/history and claims audited; historical evidence preserved.
- [x] English heuristic removed as primary V3 methodology; separate nonsense and unsafe classes implemented.
- [x] Rerunnable scoring, structured provenance, logs and tests implemented.
- [x] Human/kappa claims audited and superseded.
- [x] Back-translation investigated with real calls and failures documented.
- [x] Input intervention, fixed variants and resource adaptation implemented as bounded pipelines.
- [ ] Corrected semantic benchmark, validated accuracy and meaningful intervention effects: **blocked**, not complete.
- [ ] Native-speaker annotation, semantic translation validation and evaluation-ready resources: **not performed/released**.
