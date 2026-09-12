# Scientific claim corrections

This notice supersedes unsupported statements in historical reports, slide decks and the archived README. Those originals are retained unchanged for provenance, **not endorsed as current findings**.

| Historical claim | V3 disposition | Evidence / correction |
|---|---|---|
| 1,120 evaluated prompts | Corrected | 40 seeds, 280 prompt-language variants, 1,120 response records; not 1,120 distinct prompts. Strict CSV joins support these counts. |
| V2 fixed the evaluation | Narrowed | `f8155c1` fixed dropping unclear rows, changed them to partial and disabled LLM calls. Language/quality validity remained defective. |
| V2 ASR 50.1% | Retained only as historical heuristic fraction | 561/1,120 stored labels. Not validated harmfulness; byte-preserving current replay gives 564 because of line endings. |
| Human annotators assigned all harm scores; human-validated dataset | Withdrawn as established fact | No annotation records, IDs, score columns or scoring computation support it. Early `judge_scores.csv` merely says “Judge outputs + manual verification”; raw-response placeholder merely says “All model responses”. |
| Cohen's kappa 0.82 / 10% human spot-checks | Withdrawn | No paired ratings, protocol or reproducible statistic. No replacement value invented. |
| Native-speaker translations validated semantic equivalence | Unverified, removed from current description | Translation helper uses Google and has incorrect xh mapping. Private processes cannot be ruled out, but artifacts do not establish them. |
| Heuristic + functioning LLM judging | Corrected | Current fallback is constant partial. Eleven stored rows labeled llm do not prove API judging occurred. |
| Temperature .7, max_tokens 2048 | Unverified historically | Current helper uses 0/512. Stored files lack enough metadata to resolve actual settings. |
| First comprehensive / first systematic evidence | Removed | No priority claim is needed or established. Regional coverage and transparent methodology are the defensible contribution. |
| Significant safety gap / catastrophic model rankings | Withheld pending semantic rescoring | Language-sensitive heuristic plus response-quality and translation confounds. Legacy tests ignore pairing. |
| Morphology/tokenization causes failures; MoE transfers safety better | Removed as conclusions | No controlled mechanistic/white-box experiment. At most hypotheses for future work. |
| Gibberish is rare; partial content equally dangerous | Unsupported | 382 rows are repetition-truncated, but neither this status nor partial label proves semantic nonsense or danger. |
| “Code-switch vulnerability” metric / dashboard | Corrected | Existing metric is a monolingual language gap. V3 English-wrapper family is a planned new intervention, not a measured effect. |
| >90% includes 90.0%; GPT safest although Kimi has lower ASR | Historical inconsistencies flagged | Threshold arithmetic and ranking definitions were inconsistent; no new ranking is endorsed. |
| V3 has corrected results | Narrowed | V3 has corrected architecture and measured audit findings; corrected semantic ASR is unavailable. |
| V3 translation preserves meaning / reduces ASR | Not claimed | 1/240 round trips, zero semantic comparisons, zero paired target outcomes. |

## Newly supported findings
- Exact all-row joins, historical label counts and status/label contingency are reproducible.
- Three classifications are sensitive to embedded CRLF versus LF because of length thresholds.
- 319/561 historical apparent successes are flagged repetition-truncated; the true false-positive fraction is unknown.
- Full-text structured semantic scoring, content-keyed caches, explicit uncertainty and immutable V3 outputs are implemented.
- 22 software contract tests pass; this is not a multilingual accuracy score.

Historical citations, model parameter counts and provider-training characterizations were not independently verified in V3 and are not used to support V3 conclusions. No new citation or human agreement number has been fabricated.
