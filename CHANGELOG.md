# Changelog — maturity-components

All notable changes to this repository are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-11-13

### Fixed

- The manifest now declares `type: component`, matching the registration record for this asset. The registry's `registration.schema.json` and assessment-ci's `model-manifest.schema.json` now agree on the `component` asset type (assessment-ci PR #6), so the manifest is schema-valid and the Level 3 ecosystem coherence check passes.
- Level 1 validation now asserts `model.yaml` declares `type: component`, so a future drift is caught locally instead of at Level 3.

### Notes

- No component package content changed. The four dimension packages and the component index are byte-identical to v1.0.0.
- The prior mismatch was latent since the registration record was written on 2026-10-31. It was masked because the source repository returned HTTP 404, so the ecosystem validator classified this asset as "legacy/umbrella" and skipped the coherence check entirely.


## [1.0.0] — 2026-11-13

### Added

- Initial release of the `maturity-components` maturity model as an
  independently versioned asset, per the Assessment-Models organisation
  taxonomy (CR-AM-11 §8).
- Model-owned scale conforming to the published `maturity-scale.schema.json`:
  five levels, ordinals 0–4, `ordering: ascending`, linear topology with
  exponential progression, scored against the canonical v2 band instance
  (`dea:maturity-bands-v2` v1.0.0) — non-linear widths 20/25/25/18/12 and
  per-level effort multipliers 1.0 → 6.0.
- CR-AM-11 §15 contract handshake (`model.yaml`) declaring conformance to
  `maturity-scale-contract`, `maturity-model-contract` and
  `conformance-contract` against `technehub-labs/dea-metamodel`.
- Level 1 local model CI and Level 2 contract conformance workflows.
- Worked scoring example demonstrating canonical v2 band resolution and the
  effort-adjusted value.

### Notes

- Level semantics are carried verbatim from the authoritative source; only the
  scoring fields differ between the frozen v1-alpha lineage and the canonical
  v2 scheme.
