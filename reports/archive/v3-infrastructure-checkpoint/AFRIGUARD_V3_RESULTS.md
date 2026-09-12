# AfriGuard V3 results

**Status: methodological upgrade with blocked semantic inference, not a completed corrected benchmark.**

## Reconstructed historical baseline
Source: `results/v3/audit/baseline.json`, row-level reproduction and preserved V1/V2 documents.

| Model / aggregate | V1 reported % | V2 stored % | V3 semantic % | V3−V2 |
|---|---:|---:|---:|---:|
| Overall | 60.6 | 50.0893 | unavailable | unavailable |
| GPT | 42.1 | 35.3571 | unavailable | unavailable |
| Kimi | 70.9 | 32.1429 | unavailable | unavailable |
| Llama | 54.1 | 54.2857 | unavailable | unavailable |
| Qwen | 80.6 | 78.5714 | unavailable | unavailable |
| English | 26.6 | 24.3750 | unavailable | unavailable |

A recovered pre-correction CSV at `5e52f94:analytics/evaluation.csv` has **952 data rows**, not 953 (953 includes the header). Its 565/952 micro rate is 59.3487%, different from the report's 60.6%. All 168 missing records are blocked-status records; V2 additionally changed eleven shared LLM-labeled records to partial (four compliance, seven refusal). The recovered artifact→V2 stored difference is −9.2595 pp; this is distinct from the report-to-report comparison. `results/v3/history/summary.json` and the byte-preserved deleted audit report substantiate these facts.

V1→V2 reported overall difference: −10.5 pp (−17.3% relative to the rounded V1 rate). V1's DOCX also reports 61.9% in its distribution table, so its headline cannot be treated as a unique reproducible result. V2's reported 50.1% is correctly rounded from its stored label counts. These are historical heuristic labels, not validated safety measurements.

The exact current legacy replay yields 564/1,120=50.3571%, rather than 561/1,120, because three embedded-CRLF responses cross a length threshold. The initial universal-newline audit reproduced 561 exactly; the stricter audit corrected that preliminary statement. A pandas check confirms CRLF preservation. This +0.2679 pp difference is a serialization artifact, not a semantic correction.

## Apparent unsafe compliance and quality flags
| Stored status | n | Old compliance | Old partial | Old refusal |
|---|---:|---:|---:|---:|
| ok | 561 | 242 | 120 | 199 |
| repetition_truncated | 382 | 319 | 57 | 6 |
| blocked | 168 | 0 | 168 | 0 |
| off_topic | 9 | 0 | 8 | 1 |

319/561 apparent successes (56.86%) are repetition-truncated. This identifies a large potentially confounded subset; **it does not establish a 56.86% false-positive rate**. Even the 242 status-ok successes need semantic review. Language mismatch, partial content and actual nonsense cannot be quantified reliably from stored status alone. Do not subtract all truncated rows from the numerator and call the result corrected ASR.

## V3 scoring output
`results/v3/core-offline/scored_responses.jsonl` retains all 1,120 original records with source/hash/provenance and explicit pending AMBIGUOUS labels. Coverage 0/1,120. Primary semantic ASR, V3−V2 difference, relative difference and bootstrap CI: **null**. Unresolved bounds [0,1] are vacuous missing-evidence bounds, not confidence intervals. Genuine unsafe compliance, safe refusals and nonsense counts remain unmeasured, not zero.

The 112-record validation manifest exists; paired semantic cross-checks completed: 0. Agreement: null. No human or automated accuracy claim is supported by mocked software tests.

## Back-translation
One of 240 non-English inputs returned a translation: `11_nso`. Surface Jaccard 0.7333, character similarity 0.9173, length ratio 1.0152; no numeric-token mismatch. No semantic preservation review completed. Remaining 239 requests failed; provider diagnostic probes found an HTTP-200 page containing a Google server error, and HTTP 429 on an alternate endpoint. This heavily incomplete sample cannot support language comparisons or quantify translation drift.

## Intervention and attack pilots
480 tasks planned from four prespecified seeds, six languages, four model IDs and five arms. The single back-translation belongs to the selected pilot, giving four translation-arm tasks ready and 92 blocked. Direct, English baseline, English-wrapper and lowercase tasks are specified. Target calls completed: 0; API access unavailable. No measured mitigation, code-switch or orthographic effect; all effect sizes and uncertainty are null. The 192 non-translation variant tasks are plans, not tested jailbreaks.

## Safety-resource prototype
24 benign resource candidates; first three translation attempts failed and circuit breaker skipped remaining requests. Zero completed round trips; zero evaluation-ready resources. Source text and quarantine reasons preserved. No training or target safety evaluation occurred.

## Engineering validation
22 new tests pass; required multilingual/refusal/nonsense/compliance scenarios are mocked contract tests, not empirical accuracy tests. The baseline checkout had no discoverable test suite. Four live Kimi calibration cases were recovered from deleted history; they were not executable here because of missing KIMI_API_KEY/SDK and a hard-coded Windows path. All source files compile. Offline scorer reruns are deterministic and historical data hashes are checked separately in final QC. See the experiment log and final QC artifact for exact commands/status.

## Supported conclusion
The V2 headline measures a language-sensitive heuristic with collection-quality and serialization confounds. V3 makes these defects and missing evidence explicit, replaces the primary scoring architecture, and provides reproducible controlled-experiment scaffolding. It does **not yet establish** a corrected safety gap, model ranking or successful mitigation.
