# perf-results — measurements, not baselines

Append-only store of perf **measurements** for `raeq/translit` (#234).

Each line of `measurements.jsonl` is one fingerprinted record emitted by
`scripts/perf_fingerprint.py` (schema `translit-perf-fingerprint/v1`).

**These are measurements, NOT baselines.** A record is comparable to another
**only within an identical fingerprint bucket** — same `corpus_digest`, same
`build.arch`, same `cpu.microarch`, same `cpython`. Absolute numbers never
transfer across machines; comparator ratios are valid only bucketed as above.
Never treat a value here as a cross-machine baseline, and never copy one into the
source tree (the source tree carries zero committed absolutes — gate V17).
