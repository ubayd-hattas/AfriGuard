# Translation validation — V3

## Questions
Do stored translations preserve original meaning, harmful intent, category, objective, entities, severity and instruction structure? Does input translation before target generation change unsafe compliance? These require different experiments.

## Historical evidence
Current translator incorrectly maps xh→ss (Swati), lacks st/nso and has invalid default ss. Actual stored prompts are identical across all four models, but their original translation system/native-speaker provenance is not verifiable. The code bug does not prove that stored xh text is Swati. The recovered earlier 200-row benchmark uses en/zu/af/ss/ts, with all 160 IDs shared with current data matching exactly. Its Swati rows do not establish the provenance of the later xh/st/nso conditions. V3 uses correct xh/st/nso mappings and checks provider language support. English seeds are preserved as comparison sources, not substitutes for failed back-translations.

## Executed experiment
- 240 stored non-English inputs (40 per language) sent for Google back-translation via deep-translator 1.11.4.
- Four bounded workers, 20-second HTTP timeout, up to two attempts/text.
- A benign Afrikaans refusal probe succeeded before the batch; this was only a connectivity probe, not scorer validation.
- All six language codes were supported by the library's advertised map.
- Results: af 0/40, nso 1/40, st 0/40, ts 0/40, xh 0/40, zu 0/40. Overall 1/240 (0.42%).
- Only `11_nso` succeeded; its full translated text and cache metadata are preserved under `results/v3/back_translation/` and `results/v3/cache/translation/`.
- Token Jaccard 0.733333; character SequenceMatcher 0.917293; length ratio 1.015152; numeric-token sets equal.
- Semantic comparisons completed: 0 (no judge credential).

## Failure diagnosis and fallback
A direct failing-request diagnostic returned HTTP 200 but an HTML page containing Google's Error 500, without either result-container or t0 translation elements. Therefore TranslationNotFound is not evidence that a language is untranslatable or that the prompt semantics were invalid. One alternative Google endpoint probe returned HTTP 429. No bypass of that rate limit was attempted. Resource translation also failed on benign content. No paid API or alternative model was silently introduced.

The initial full batch retried failures independently; following diagnosis, a three-failure circuit breaker was added for future translation runs (up to four already-running workers may finish). Successful cache entries remain reusable. Failures are preserved in immutable run artifacts but are not treated as successful cached translations. New retries must use new output paths.

## Interpretation
No defensible estimate of semantic drift, language fidelity or impact on the historical safety gap can be made from this result. Surface similarity cannot detect negation, objective or severity changes reliably; a unit test demonstrates high character similarity despite negation removal. Equality of numeric-token sets does not establish entity preservation. No significance test or confidence interval for semantic fidelity is appropriate with only one available, nonrandom success.

## Reproduction / completion
Install `requirements-v3-translation.txt`, then run `python scripts/v3_translation.py --out results/v3/back_translation-retry --workers 1`. Cached `11_nso` is reused. Remote semantic review is not currently permitted because no approved reproducible judge exists; follow [the blocked judge gate](JUDGE_GATE_BLOCKED.md) before any future judged run. Automated review would still remain unvalidated until native-speaker checks. Prefer a reliable authorized translation service or independently reviewed offline translations if the free transport remains unavailable.

`v3_validate.py` separately translates responses and prompts for a scorer cross-check; it did not run translations because primary judgments were unavailable. `v3_experiments.py` instead translates only model INPUT before target generation, and compares all arms generated under matched new settings. No effect for either pathway has been measured.
