# translit

**Fast Unicode transliteration, slugification, and text normalization — powered by Rust.**

translit is a single, MIT-licensed Python package that replaces a constellation of legacy Unicode text-processing libraries — [Unidecode](https://pypi.org/project/Unidecode/), [text-unidecode](https://pypi.org/project/text-unidecode/), [python-slugify](https://pypi.org/project/python-slugify/), [awesome-slugify](https://pypi.org/project/awesome-slugify/), [anyascii](https://pypi.org/project/anyascii/), [confusable_homoglyphs](https://pypi.org/project/confusable-homoglyphs/), [pathvalidate](https://pypi.org/project/pathvalidate/), and more — with a single, coherent API backed by compiled Rust.

---

## Why translit?

| | Legacy libraries | translit |
|---|---|---|
| **Performance** | Pure Python | Rust via PyO3 — [see benchmarks](performance.md) |
| **License** | Mixed (GPL, Artistic, MIT) | MIT |
| **API surface** | 8+ packages, 8+ APIs | One package, one API |
| **Unicode coverage** | Varies widely | Comprehensive, consistent tables |
| **Language awareness** | Limited or none | 64 built-in language profiles |
| **Type safety** | Partial or missing | Full py.typed + stub coverage |

---

## Installation

```bash
pip install translit-rs
```

Wheels are available for Linux, macOS, and Windows on Python 3.9+.

---

## Quick start

### Transliterate Unicode to ASCII

```python
from translit import transliterate

transliterate("Ünïcödé téxt")       # => "Unicode text"
transliterate("北京市")              # => "bei jing shi"
transliterate("Ü", lang="de")       # => "Ue" (German rules)
transliterate("Москва", lang="auto")  # => "Moskva" (auto-detects Russian)
```

### Generate URL-safe slugs

```python
from translit import slugify

slugify("My Blog Post!")             # => "my-blog-post"
slugify("Ärger im Büro", lang="de") # => "aerger-im-buero"
```

### Detect and normalize confusable characters

```python
from translit import is_confusable, normalize_confusables

is_confusable("Неllo")              # => True (Cyrillic Н)
normalize_confusables("Неllo")      # => "Hello"
```

### Sanitize filenames

```python
from translit import sanitize_filename

sanitize_filename("my<file>:v2.txt")  # => "my_file_v2.txt"
```

### Compose a text-cleaning pipeline

```python
from translit import TextPipeline

pipe = TextPipeline(
    normalize="NFC",
    confusables=True,
    strip_accents=True,
    fold_case=True,
    collapse_whitespace=True,
)
pipe("  Héllo\u200b Wörld  ")  # => "hello world"
```

---

## User Guide

Core concepts and usage for each feature area.

- **[Getting Started](user-guide/getting-started.md)** — Installation, first steps, and basic usage
- **[Transliteration](user-guide/transliteration.md)** — Unicode → ASCII with 64 language profiles
- **[Slugification](user-guide/slugification.md)** — URL-safe slug generation, drop-in python-slugify replacement
- **[Normalization](user-guide/normalization.md)** — NFC / NFD / NFKC / NFKD Unicode normalization
- **[Confusable Detection](user-guide/confusables.md)** — TR39 homoglyph detection and normalization
- **[Filename Sanitization](user-guide/filenames.md)** — Cross-platform safe filenames
- **[Text Cleaning](user-guide/text-cleaning.md)** — Accent stripping, case folding, whitespace collapse
- **[Grapheme Clusters](user-guide/graphemes.md)** — User-perceived character counting, splitting, and truncation
- **[Text Pipeline](user-guide/pipeline.md)** — Composable, pre-compiled multi-step processing
- **[Language Support](user-guide/language-support.md)** — 64 built-in profiles, auto-detection, custom profiles
- **[Language Detection](user-guide/language-detection.md)** — How `lang="auto"` works: script identification, character-level discrimination, fail-safe fallbacks

---

## Guides by Role

Task-oriented guides for specific use cases and audiences.

- **[For Data Engineers](data-engineer-guide.md)** — ETL normalization, deduplication, encoding detection, batch processing
- **[For ML / LLM Pipelines](ml-pipeline-guide.md)** — Text preprocessing, emoji handling, TextPipeline
- **[For Web Developers](web-developer-guide.md)** — URL slugs, filename sanitization, form cleaning
- **[For Security Engineers](security-guide.md)** — Homoglyph detection, IDN validation, input canonicalization
- **[For Librarians & Catalogers](librarian-guide.md)** — Catalog keys, title dedup, sort normalization
- **[For Scholars & Linguists](scholarly-guide.md)** — ISO 9, script analysis, transliteration profiles
- **[Docker](docker.md)** — CLI usage via Docker container

---

## API Reference

Complete function signatures, parameters, and return types.

- **[Overview](api/index.md)** — API reference index
- **[Core Transforms](api/transforms.md)** — `transliterate`, `slugify`, `normalize`, `sanitize_filename`, `strip_accents`, `strip_zalgo`, `fold_case`, `collapse_whitespace`, `demojize`, `strip_bidi`, batch APIs
- **[Precompiled Pipelines](api/pipelines.md)** — `security_clean`, `ml_normalize`, `catalog_key`, `display_clean`, `search_key`, `sort_key`, `sanitize_user_input`, `PRESETS`
- **[Classes](api/classes.md)** — `Text`, `Slugifier`, `UniqueSlugifier`, `TextPipeline`, compatibility aliases
- **[Predicates](api/predicates.md)** — `detect_scripts`, `is_mixed_script`, `is_confusable`, `is_ascii`, `is_normalized`, `is_zalgo`, `is_safe_hostname`
- **[Grapheme Clusters](api/graphemes.md)** — `grapheme_len`, `grapheme_split`, `grapheme_truncate`
- **[Encoding Detection](api/encoding.md)** — `detect_encoding`, `decode_to_utf8`
- **[Language Profiles](api/language-profiles.md)** — `list_langs`, `register_lang`, `register_replacements`
- **[Enums & Types](api/enums.md)** — `Script`, `NF`, `EmojiProvider`, type aliases, language constants
- **[Exceptions](api/exceptions.md)** — `TranslitError`

---

## Reference

- **[Language Reference](reference.md)** — All 64 languages: codes, names, reference texts, and per-language transliteration rule tables

---

## Architecture

Internal design documentation for contributors and advanced users.

- **[Transliteration Engine](architecture/transliteration-engine.md)** — PHF lookup, language table chain, Indic virama handling
- **[Data Tables](architecture/data-tables.md)** — TSV format, build.rs code generation, compile-time PHF
- **[Pipeline](architecture/pipeline.md)** — TextPipeline internals, execution order, step bitflags
- **[Emoji Engine](architecture/emoji-engine.md)** — Emoji detection, provider system, pure-Rust path
- **[Emoji Plugins](architecture/emoji-plugins.md)** — EmojiProvider protocol, custom providers
- **[Security](architecture/security.md)** — Confusable detection, hostname validation, bidi stripping
- **[Performance](architecture/performance.md)** — Optimization strategies, PHF tables, batch amortization

---

## Performance

- **[Performance Overview](performance.md)** — Benchmark methodology, results, and optimization details
- **[Benchmark Suite](benchmarks.md)** — How to run benchmarks, Criterion and timeit configurations

---

## Migration Guides

Parameter-compatible replacements for existing libraries.

- **[Migration Overview](migration/index.md)** — Feature comparison matrix
- **[From Unidecode / text-unidecode](migration/from-unidecode.md)** — Drop-in `unidecode()` alias
- **[From python-slugify / awesome-slugify](migration/from-python-slugify.md)** — Parameter-compatible `slugify()`
- **[From confusable_homoglyphs](migration/from-confusable-homoglyphs.md)** — Script detection and normalization
- **[From pathvalidate](migration/from-pathvalidate.md)** — Filename sanitization
- **[From anyascii](migration/from-anyascii.md)** — Language-aware transliteration

---

## Other

- **[Limitations](limitations.md)** — Known constraints, edge cases, and design trade-offs

---

## License

translit is released under the [MIT License](https://github.com/raeq/translit/blob/main/LICENSE).
