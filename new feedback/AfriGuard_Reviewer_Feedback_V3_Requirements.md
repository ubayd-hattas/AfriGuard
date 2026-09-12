# AfriGuard — Reviewer Feedback & V2 Upgrade Requirements

## Purpose

This file consolidates the reviewer feedback received after the AfriGuard hackathon submission. It is intended to be read by an AI coding/research agent working on the existing repository and used as the requirements baseline for a post-hackathon V3-quality upgrade.

## Project context from the submitted work

- Project: AfriGuard
- Goal: evaluate whether LLM safety behavior differs between English and South African / African low-resource languages.
- Original evaluation scale: 4 frontier LLMs × 7 languages × 40 prompts = 1,120 model responses.
- Harm categories were selected for the South African context, including SASSA/financial fraud, xenophobic incitement, gang recruitment, and political disinformation.
- The project released an evaluation dataset and pipeline.
- The project had a V2 correction/erratum after a bug was noticed following the hackathon submission.
- The V2 changes happened BEFORE the reviewers' feedback below. Therefore, the current repository must be audited rather than assuming the reviewed version and current version are identical.
- An important methodological issue identified after submission is that the original refusal scoring relied on English refusal/no-word detection. This can incorrectly label an African-language response as a successful jailbreak merely because it does not contain an English refusal phrase.
- The project also contains claims/descriptions about human scoring and an inter-annotator reliability value that, according to Reviewer 4, are not supported by the actual implementation and should not be presented as having happened unless the repository contains verifiable evidence.

## Reviewer consensus

The project is considered useful and relevant, particularly because:
1. It evaluates safety in a realistic South African context.
2. The evaluation covers multiple African/low-resource languages and multiple models.
3. The released dataset and pipeline make the work reproducible and reusable.
4. The topic has practical implications for systems such as banking and government chatbots.
5. The main headline finding — low-resource languages can have weaker safety behavior — is important but is NOT sufficiently novel by itself because prior literature already reports similar effects.

The strongest future contribution should therefore be:
- methodological rigor,
- South African/African language coverage,
- a corrected and validated evaluation methodology,
- an openly reusable pipeline/dataset,
- and new experiments that go beyond simply reproducing the known multilingual safety gap.

---

# Reviewer 1

### Positive feedback
- Solid work grounded in a realistic regional context.
- Good evaluation scale: 1,120 responses across 4 models, 7 languages, and 40 prompts.
- Harm categories were thoughtfully adapted to South African realities rather than being generic.
- Transparency about mistakes was a strength.
- The erratum/V2 correction demonstrated integrity.
- Open release of the pipeline was considered useful.

### Requested future work
1. Test whether interventions other than fine-tuned classifiers can reduce the safety gap.
2. Test a translate-to-English pipeline:
   - Translate the African-language input into English.
   - Run the safety/model pipeline.
   - Determine whether the attack-success rate drops.
3. Explore novel attack vectors rather than relying only on translation-based attacks.

---

# Reviewer 2

### Requested future work
Design an automated pipeline that can:
- take English-language safety datasets,
- take English adversarial-training pipeline code and/or safety-classifier resources,
- translate/adapt them into African languages,
- and make the resulting resources usable for multilingual safety evaluation/training.

This suggests a potentially strong direction for AfriGuard V3:
- English safety resource → multilingual adaptation → evaluation/validation → African-language safety resource.

---

# Reviewer 3

### Positive feedback
- The topic has meaningful real-world stakes.
- South African-language safety evaluation matters for banking, government, and other deployed systems.
- The open dataset and pipeline are major strengths.
- The project covered substantial ground in a short time.

### Required methodological improvements
1. Reframe the novelty:
   - Do NOT claim that discovering a multilingual safety gap is itself a novel discovery.
   - Position the contribution around South African coverage, the released dataset, the evaluation pipeline, methodological validation, and any genuinely new intervention/attack results.

2. Add a back-translation check:
   - Back-translate African-language prompts/responses into English.
   - Use this to test whether observed safety differences are actually caused by translation noise or semantic drift.
   - Prefer a systematic quantitative comparison rather than anecdotal inspection.

3. Clarify the scoring pipeline:
   - Explicitly separate automated/LLM-judge scoring from human scoring.
   - Document exactly which component produced every score.
   - Do not imply human evaluation occurred unless there is reproducible evidence that it did.

4. Treat small per-category samples cautiously:
   - Per-category results should be described as exploratory/hypothesis-generating when sample sizes are small.
   - Report uncertainty where feasible.
   - Avoid overstating individual category differences.

---

# Reviewer 4

## Critical issue: original scoring methodology

The reviewer identified the most serious methodological problem:

The original scoring tool reportedly detects English refusal/no words. This is not a valid language-independent jailbreak/harm classifier.

Potential failure mode:
- A model gives a safe refusal in an African language.
- The refusal does not contain the English refusal words being searched for.
- The scorer marks the response as a successful jailbreak.
- Alternatively, a model outputs gibberish/nonsense.
- The scorer can also count that as a successful jailbreak because it lacks the English refusal marker.

Therefore:

**The original headline attack-success numbers must NOT be treated as reliable until the responses are re-scored with a language-aware methodology.**

## Required response to this issue

1. Preserve the original V1/V2 results for provenance.
2. Do not silently overwrite historical results.
3. Create a corrected/reproducible scoring pipeline.
4. Separate at minimum:
   - harmful/unsafe compliance,
   - safe refusal,
   - nonsense/gibberish/broken response,
   - ambiguous/uncertain cases.
5. Score responses using a language-aware method.
6. Validate the automated scorer against a manually checked sample if feasible.
7. If native-speaker validation is unavailable, use a translation-based approach plus explicit validation/limitations.
8. Quantify disagreement between automated and manual/validated labels where validation is performed.
9. Recompute all headline metrics from the corrected labels.
10. Clearly distinguish:
    - original V1/V2 metrics,
    - corrected V3 metrics,
    - and any metrics that remain provisional.

## Human scoring / reliability claim

Reviewer 4 also stated that the repository code does not support the report's claims that:
- human scorers performed the evaluation, and
- a reliability value of 0.82 was obtained.

Therefore:
- Audit the repository for evidence of actual human annotation.
- If there is no evidence, remove or correct those claims.
- Never fabricate or retroactively imply human annotation.
- If a new human-validation stage is actually performed, document it separately as new V3 work, including sampling methodology and agreement statistics.

---

# Consolidated V3 requirements

The AI agent should treat the following as the priority order.

## P0 — Audit before changing anything

1. Inspect the entire current repository.
2. Read README, documentation, reports, notebooks, scripts, configuration, data schemas, tests, experiment logs, Git history, branches/tags if locally available, and V2/erratum material.
3. Determine exactly what changed between the original submission and V2/current state.
4. Identify the exact current scoring implementation.
5. Trace how every reported metric is generated.
6. Identify any unsupported claims in the report.
7. Establish a reproducible baseline from the current code before modifying it.

Do not assume that reviewer descriptions exactly match the current V2 implementation.

## P1 — Fix scoring validity

Build a language-aware scoring pipeline that can distinguish:
- unsafe/harmful compliance,
- refusal/safe response,
- nonsense/gibberish/broken output,
- ambiguous/uncertain output.

The pipeline must not rely on English refusal-word matching as the primary criterion.

Preferred approach:
- use a validated multilingual judge or translation-based scoring mechanism;
- if translation is used, evaluate translation quality/semantic preservation;
- retain raw responses and intermediate translated/judged artifacts;
- make scoring reproducible and auditable.

If native-speaker validation is practical within available resources, use it for a sampled validation set. If it is not practical, proceed with a translation-based validation design and clearly mark the limitation.

## P2 — Back-translation / semantic validation

Implement a back-translation experiment to test whether:
- the original English prompt,
- its African-language translation,
- and the back-translated English version

retain sufficiently similar meaning.

Quantify semantic/translation drift where possible.

Do not merely state that translation noise is unlikely; produce evidence.

## P3 — Recompute the core results

Using corrected scoring:
- rerun the relevant evaluation/scoring pipeline;
- recompute attack-success/harm metrics;
- compare V1/V2/original metrics with corrected V3 metrics;
- report changes transparently;
- compute uncertainty/confidence intervals where statistically appropriate;
- avoid overinterpreting small per-category samples.

The corrected results become the primary scientific results, while old results remain as historical/provenance results.

## P4 — Test translation-to-English intervention

Design an experiment that tests whether translating African-language prompts into English before safety processing/model interaction changes safety outcomes.

At minimum compare:
1. direct African-language interaction;
2. African-language → English → safety/model pipeline;
3. where meaningful, an English baseline.

Measure whether the translate-to-English pathway reduces harmful compliance / attack success.

Document exactly what is being translated and where translation occurs in the pipeline.

## P5 — Explore novel attack vectors

Do not make translation the only attack strategy.

Design a small but meaningful set of novel multilingual attack variants, chosen using reasonable research assumptions and constrained by safety and compute budget.

Potential categories to investigate include:
- code-switching between English and an African language;
- orthographic variation;
- colloquial/slang variants;
- transliteration;
- paraphrasing;
- culturally localized framing;
- indirect or multi-turn attacks;
- mixed-language prompt structures.

The agent should choose the most scientifically defensible subset rather than implementing every possible idea.

## P6 — Investigate automated multilingual safety-resource generation

Prototype the Reviewer 2 direction where useful:

English safety resource
→ translation/adaptation
→ African-language resource
→ automated validation
→ evaluation-ready artifact.

This can include:
- multilingual safety prompts,
- adversarial examples,
- classifier/judge prompts,
- or other evaluation resources.

Do not expand scope excessively if it compromises the critical scoring correction. Treat this as a secondary experiment/prototype after P0–P5.

## P7 — Reporting and reproducibility

Update documentation so a researcher can reproduce the V3 evaluation.

The final project should make clear:
- what was done originally;
- what V2 fixed;
- what reviewers identified;
- what V3 fixes;
- which results are historical vs corrected;
- how scoring works;
- how translation/back-translation was validated;
- what is automated vs human-validated;
- limitations;
- exact datasets/models/prompts/configuration where legally/API-policy appropriate.

---

# Scientific integrity rules

The agent must follow these rules throughout the upgrade:

1. Never fabricate experiments, human annotations, model outputs, scores, or citations.
2. Never claim human validation unless actual human validation evidence exists.
3. Never overwrite old results without preserving provenance.
4. Never silently change the definition of a metric.
5. Every headline metric must be traceable to raw data and code.
6. If a requested experiment cannot be completed because of API access, model availability, cost, rate limits, or missing data, record the limitation and implement the best reproducible alternative.
7. Prefer a smaller rigorous experiment over a larger invalid one.
8. Keep raw model responses immutable where possible.
9. Make assumptions explicit in machine-readable experiment metadata.
10. Separate exploratory findings from statistically well-supported conclusions.
11. Treat small category-level samples as uncertain.
12. Do not optimize specifically for producing an impressive number; optimize for methodological validity and reproducibility.
13. Preserve an audit trail of every major change.
14. Use versioned outputs rather than replacing evidence in place.

---

# Suggested V3 artifact structure

A robust implementation should, where compatible with the existing repository, produce artifacts resembling:

- `reports/AFRIGUARD_V3_METHODOLOGY.md`
- `reports/AFRIGUARD_V3_RESULTS.md`
- `reports/AFRIGUARD_V3_LIMITATIONS.md`
- `reports/SCORING_AUDIT.md`
- `reports/TRANSLATION_VALIDATION.md`
- `reports/EXPERIMENT_LOG.md`
- `results/v3/`
- `results/v3/scored_responses/`
- `results/v3/back_translation/`
- `results/v3/interventions/`
- `results/v3/novel_attacks/`
- `configs/v3/`

These are suggestions, not mandatory paths. Preserve the repository's existing conventions when they are better.

---

# Definition of success

AfriGuard V3 should be substantially stronger than the hackathon submission even if the corrected headline attack-success rate becomes smaller.

A successful upgrade should demonstrate:

1. The original scoring bug is identified and corrected.
2. Current code/data/results are fully audited.
3. Historical V1/V2 results remain preserved.
4. Corrected language-aware scores are reproducible.
5. Gibberish/broken outputs are separated from genuine harmful compliance.
6. Translation/back-translation effects are quantitatively investigated.
7. At least one intervention is tested, especially translate-to-English.
8. At least one non-translation multilingual attack vector is tested if feasible.
9. Human-vs-automated scoring claims are scientifically accurate.
10. The final report makes a narrower but stronger contribution claim centered on African/South African coverage, dataset/pipeline quality, and validated methodology.
11. All conclusions are supported by the actual evidence produced by the repository.

## Reviewer feedback, in one sentence

The project has a strong and worthwhile foundation, but the next version needs to replace the English-only refusal heuristic with validated language-aware scoring, separate gibberish from genuine jailbreaks, verify translation effects, test stronger interventions and novel attack vectors, and make the scientific claims match exactly what the code and evidence demonstrate.
