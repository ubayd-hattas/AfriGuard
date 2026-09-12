# V3 judge gate — BLOCKED

## Decision

**Neither tested judge is approved. V3 semantic rescoring is blocked, full semantic rescoring was not run, and no corpus semantic ASR is available.** Historical V1/V2 ASR values remain heuristic labels, not validated harmful-compliance rates.

## Evidence

### Local candidate

The installed local Qwen3 8B candidate completed 95 content-bearing judgments from the unchanged 112-record validation sample (17 records were blocked placeholders) and all 12 frozen synthetic stress cases. Only 8/12 synthetic expectations were met. In particular, it labeled two African-language refusals `UNSAFE`; independent English translation exposed the contradiction, and the same candidate labeled both translated views `SAFE_REFUSAL`. This targeted diagnostic is not human validation or an independent-judge accuracy estimate.

### Remote route

The corrected bounded access gate returned one schema-valid English refusal-control judgment. The immediately repeated identical request failed at transport. The one permitted WebSocket access-only probe also failed at transport. Thus remote execution was not reproducible, multilingual validation was not run, and the remote route is not approved.

Evidence is preserved in:

- [`SEMANTIC_VALIDATION_NEXT_STAGE.md`](SEMANTIC_VALIDATION_NEXT_STAGE.md)
- [`results/v3/next-stage/final_summary.json`](../results/v3/next-stage/final_summary.json)
- `results/v3/judge-access-gate-corrected/`

## Bounded resume gate

Do not run live remote scoring now. Resume only in this order:

1. Independently establish stable, authorized judge access.
2. Run the frozen controls and unchanged 112-record validation sample.
3. Record an explicit judge approval or rejection using the documented semantic and language-validity evidence.
4. Only after explicit approval, run the 952-record historical semantic rescore.

Never substitute `scripts/judge.py`, English keywords, response length, repetition artifacts, or missing-to-zero handling for semantic judgment. Pending and blocked records are unresolved, not safe and not zero.
