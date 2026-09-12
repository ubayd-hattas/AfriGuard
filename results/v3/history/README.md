# Recovered pre-correction evidence — historical, not V3 execution

Files in `recovered/` are byte-for-byte Git blobs from `5e52f94`, with hashes in `manifest.json`. They were deleted at `f8155c1` and are restored here only for audit/provenance. Do not run the old judge or treat its comments as validation evidence.

The evaluation CSV contains 952 records (953 lines including header), with 565 compliance labels: 59.3487% micro ASR. This does not reproduce the V1 report's 60.6%. All 168 records absent relative to V2 have blocked status. Eleven old LLM-labeled scores also changed to partial. Four old live Kimi calibration cases require missing API/SDK access and were not run during V3.

See `summary.json` and `reports/SCORING_AUDIT.md` in the repository root for the current interpretation. No human annotation or kappa is established by these artifacts.
