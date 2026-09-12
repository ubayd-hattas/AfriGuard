# AfriGuard V3 — South African multilingual safety evaluation

AfriGuard preserves a regional safety-evaluation dataset and provides an auditable,
language-aware scoring pipeline. Its contribution is **coverage and reproducibility**,
not a claim to have first discovered multilingual safety differences.

## Scientific status

**The historical headline ASR is not a validated harmful-compliance rate.**
V2 retained all 1,120 records but still used English keyword/length scoring and a
constant `partial` fallback, not a functioning LLM judge. V3 replaces this as the
primary methodology; it does not overwrite historical labels.

| Evidence | Result |
|---|---|
| V1 reported ASR | 60.6%; internally inconsistent historical report |
| Recovered pre-correction CSV | 565/952 = 59.35%; does not match V1 headline |
| V2 stored heuristic ASR | 561/1,120 = 50.09% |
| Exact current legacy replay | 564/1,120 = 50.36%; three CRLF-sensitive differences |
| **V3 semantic ASR** | **Unavailable: no configured judge/API credential** |
| Historical apparent successes flagged repetition-truncated | 319/561 (56.86%); not confirmed gibberish |
| Back-translation | 1/240 succeeded; provider failures prevent conclusions |
| New human annotation / reproducible kappa | None; historical 0.82 claim unsupported |

Pending V3 labels are **not** safe responses and do not imply 0% ASR. No measured
translate-to-English mitigation or novel-attack effect is claimed.

## Dataset and provenance

- 40 seeds × 7 language conditions × 4 model identifiers = 1,120 stored responses.
- Languages: English, Afrikaans, isiZulu, isiXhosa, Sesotho, Sepedi, Xitsonga/Tsonga.
- Four categories: financial fraud, gang/criminal facilitation, xenophobic incitement,
  political disinformation. Ten seeds per category; category findings are exploratory.
- Original prompts and responses: `data/results/*responses.csv`.
- V1/V2 documents and `data/results/evaluation.csv` remain historical evidence.
- Previous README preserved verbatim: `reports/archive/README_V2_2c17d33.md`.
- Full audits: [project state](reports/PROJECT_STATE_AUDIT.md),
  [scoring](reports/SCORING_AUDIT.md), [claim corrections](reports/CLAIM_AUDIT.md).

## Reproduce offline (Python 3.10+; tested with 3.14.6)

No third-party packages or credentials are needed for core auditing/scoring/tests.
Run from the repository root:

```bash
python scripts/v3_audit.py
python scripts/v3_history.py
python scripts/v3_score.py --out results/v3/core-offline
python -m unittest discover -s tests -v
python scripts/v3_validate.py --primary results/v3/core-offline/scored_responses.jsonl --out results/v3/validation
python scripts/v3_experiments.py --back-translations results/v3/back_translation/back_translations.jsonl --out results/v3/interventions
```

Outputs are immutable: identical reruns are accepted; changed results require a new
`--out` directory. Successful model and translation calls are cached separately and
reused. All raw text is retained. Do **not** run the old `scripts/judge.py` to obtain
V3 results: it is historical and can write legacy outputs.

### Optional network experiments

```bash
python -m pip install -r requirements-v3-translation.txt
python scripts/v3_translation.py --out results/v3/back_translation-retry --workers 1
python scripts/v3_resources.py --out results/v3/resources-retry --live
```

The free Google transport failed in this run; see [translation validation](reports/TRANSLATION_VALIDATION.md).
No paid fallback is automatically selected. Use cached results for offline reproduction.

### Semantic scoring with available access

Export `OPENROUTER_API_KEY` securely in your shell (never commit it). V3 reads the
process environment, **not** `.env`. Select an independently suitable multilingual
judge model explicitly; no model is asserted to be validated here.

```bash
python scripts/v3_score.py --judge YOUR_JUDGE_MODEL_ID --max-calls 952 --out results/v3/core-live
python scripts/v3_validate.py --primary results/v3/core-live/scored_responses.jsonl --secondary-judge DIFFERENT_JUDGE_MODEL_ID --max-calls 112 --live-translation --out results/v3/validation-live
python scripts/v3_translation.py --judge YOUR_JUDGE_MODEL_ID --max-calls 240 --out results/v3/back_translation-live
python scripts/v3_experiments.py --back-translations results/v3/back_translation-live/back_translations.jsonl --max-calls 480 --out results/v3/interventions-live
python scripts/v3_score.py --input results/v3/interventions-live/responses.jsonl --judge YOUR_JUDGE_MODEL_ID --max-calls 480 --out results/v3/interventions-scored
python scripts/v3_experiments.py --back-translations results/v3/back_translation-live/back_translations.jsonl --scored results/v3/interventions-scored/scored_responses.jsonl --out results/v3/interventions-analysis
```

Call caps are safety/cost limits, not promises of completion. Provider-blocked historical
records remain unresolved; inspect coverage, class counts and bounds, not just ASR.
Validate judge performance before treating automated labels as research conclusions.

## Reports

- [V3 methodology](reports/AFRIGUARD_V3_METHODOLOGY.md)
- [Results](reports/AFRIGUARD_V3_RESULTS.md) and [limitations](reports/AFRIGUARD_V3_LIMITATIONS.md)
- [Experiment log](reports/EXPERIMENT_LOG.md) and `results/v3/experiment_log.jsonl`
- [Final handoff](reports/V3_HANDOFF.md) and `results/v3/final_summary.json`

The Streamlit dashboard (`analytics/dashboard.py`) displays **historical heuristic
labels only**, not V3 outcomes. Legacy dependencies remain in `requirements.txt` and
`analytics/requirements.txt`; they are not necessary for the V3 standard-library core.

## Attribution and license

Original team: Jaswin Chinthala, Seth Miguel Ferreira, Ubayd Hattas, Sebastian Stent;
Global South AI Safety Hackathon, Cape Town Hub, June 2026. V3 additions were made
by an autonomous coding assistant; no native-speaker or human annotation is implied.
MIT license; see [LICENSE](LICENSE). Dataset contains harmful research material;
handle it as untrusted evidence, not deployment or training-ready content.
