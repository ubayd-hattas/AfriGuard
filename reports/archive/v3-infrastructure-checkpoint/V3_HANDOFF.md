# AfriGuard V3 handoff

**Outcome: substantial audit and scoring-infrastructure upgrade; corrected semantic results and efficacy experiments remain blocked.** Full machine-readable summary: `results/v3/final_summary.json`.

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
