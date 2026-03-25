# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `src/unicode_ranges.rs` — named constants for all Unicode codepoint ranges used
  by the library, eliminating magic numbers scattered across modules.
- `tests/test_concurrency.py` — concurrent access tests for `LANG_TABLES` and
  `HANGUL_CACHE`, plus malformed Unicode input tests.
- Code coverage reporting in CI (`pytest-cov`, XML report uploaded as artifact).
- `CLOCK$`, `KEYBD$`, `SCREEN$`, `COM0`, `LPT0` added to Windows reserved filename list.
- `casefold()` alias for `fold_case()` — matches `str.casefold()` naming.
- `remove_accents()` alias for `strip_accents()` — matches sklearn/ML ecosystem naming.
- Compatibility parameter aliases: `replacement_text`/`max_len` on `sanitize_filename()`
  (pathvalidate), `greedy`/`preferred_aliases` on `is_confusable()` (confusable_homoglyphs),
  `delimiters` on `demojize()` (emoji library).
- Data Engineer persona guide (`docs/data-engineer-guide.md`) — ETL normalization,
  deduplication, batch processing, pandas/PySpark/Airflow integration patterns.
- Complete API documentation for 19 previously undocumented exported functions:
  precompiled pipelines, grapheme clusters, encoding detection, `Text` builder,
  `is_safe_hostname`, `demojize`, `strip_bidi`, `EmojiProvider` protocol.
- Three new API reference pages: Precompiled Pipelines, Grapheme Clusters, Encoding.
- "Guides by role" section in `docs/index.md` and `README.md`.
- Performance section in `README.md` with benchmark numbers.
- `Script` enum documentation expanded from 28 to all 41 members.

### Changed
- `transliterate_impl` refactored: capacity estimation extracted to `estimate_capacity()`,
  character classification to `classify_char()`, and CJK spacing logic to
  `needs_cjk_space()`.
- All `RwLock` accesses now recover from lock poisoning using
  `.unwrap_or_else(|e| e.into_inner())` instead of silently falling through.
- Lambda closures in `_compat.py` replaced with named inner functions for clarity.
- `emoji.rs` `write!()` call no longer uses `.unwrap()` (infallible, documented with
  a `// SAFETY` comment).
- MkDocs theme switched from `material` to `readthedocs`.
- All documentation references updated from "unirust" to "translit".
- Development status promoted from Alpha to Beta.

### Fixed
- Type stub `_text.pyi` imported from wrong module name (`unirust` → `translit`).
- Type stub `_translit.pyi` missing `min_confidence` parameter on `_decode_to_utf8`.
- Type stub `_text.pyi` missing `grapheme_split`, `grapheme_truncate`, `catalog_key` methods.

### Deprecated
- `translit._compat` awesome-slugify compatibility layer (`Slugify`, `UniqueSlugify`,
  `slugify_*` instances) — planned removal in v1.0.

## [0.1.0] — 2026-01-01

### Added
- Initial release.
- Unicode transliteration for 37 language profiles.
- Slugification, normalization, confusable detection, filename sanitization.
- Emoji demojization with ZWJ sequence support.
- Backward-compatible layers for Unidecode and awesome-slugify.
