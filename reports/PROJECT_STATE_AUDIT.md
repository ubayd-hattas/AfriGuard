# Project state audit

## Scope and provenance
Audited all tracked source/configuration, README, V2 Markdown/table, extracted V1 DOCX and both slide decks, CSV schemas and all-row computational checks, local branches/history and reviewer requirements. Branch main; baseline `2c17d33` (2026-06-22). One remote-tracking main, no local tags. Initially only `new feedback/` was untracked. No notebooks, tests, real experiment logs, model weights or separate benchmark CSV in the checkout. A deep-history pass also recovered deleted pre-correction evaluation (952 rows), a 200-row earlier benchmark, an audit report, a separate Kimi judge prototype and four API calibration cases. These are archived byte-for-byte under `results/v3/history/recovered/`; no paired human annotation provenance was found.

## Data and architecture
40 English seeds, four categories ×10; four response CSVs ×280; seven language codes en/af/zu/xh/st/nso/ts. Setswana is not in this study. Each CSV has prompt_id, seed_id, language, harm_category, model, prompt, response, status. Evaluation CSV has 1,120 labels, no response or actual harm-score field. V3 reconstructs prompts from the stored inputs rather than retranslating them and silently changing the experiment. The recovered 200-row older benchmark has en/zu/af/ss/ts: all 160 IDs shared with current data have identical prompt text. Its ss entries are not evidence that current xh entries are Swati; xh/st/nso remain without recovered forward-translation provenance.

Historical outputs remain under `data/results/`, `V1 summary/`, `V2 summary/` and Git. Legacy dashboard exists despite README claiming removal; it labels monolingual translations as code-switching. Figures are generated, not checked into current tree. README paths and commands include nonexistent report and generator names.

## Translation defects
`scripts/translate_variants.py` maps xh to Google's ss (Swati), omits st and nso, defaults to unsupported ss and requires arguments despite argument-free README instructions. Current stored xh inputs are not proven to have come from this helper: do NOT relabel them as Swati solely from code. Native-speaker translation/validation provenance is unavailable. A V3 mapping must use xh→xh, st→st, nso→nso and check actual provider support.

## Generation discrepancy
Documentation says temperature .7/max_tokens 2048; `pipeline_utils.call_model` uses 0/512. Actual stored generation settings cannot be reconstructed confidently from current code. `run_models.py` writes one excluded response filename whereas current judge reads four model-specific files. Missing finish reasons prevent distinguishing provider truncation from postprocessing. Stored repetition-truncated status indicates existing processing; these are not guaranteed unmodified provider payloads.

## Environment and reproducibility
Python 3.14.6; pandas available; requests, dotenv, deep-translator, torch and transformers initially unavailable. No repository .env or OPENROUTER_API_KEY; no local judge/model weights identified. Current-checkout unittest discovery returned no tests (exit 5). Four deleted historical calibration cases require unavailable KIMI_API_KEY/OpenAI SDK and a hard-coded Windows import path; they were inspected but not claimed to have run. Main requirements omit deep-translator and SciPy (the latter is in analytics requirements). V3 offline pipeline uses standard library only; optional translation uses existing project's deep-translator approach. Paid inference is explicitly gated and bounded, never silently invoked.

## Decisions
Prioritize preserved evidence, strict joins, full-text judgment, uncertainty and runnable missing-access handling over unsupported quantitative claims. No history rewrite or commits of user feedback. Do not expand to adaptive harmful attack optimization. Small fixed code-switch wrapper and orthographic controls will be planning artifacts unless actual paired target calls and scoring can be completed. References/model architecture claims in historic reports were not independently bibliographically validated and are not repeated as V3 findings.
