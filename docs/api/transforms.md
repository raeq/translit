# Core Transforms

Functions that transform text. All are pure functions — they never mutate the input.

## transliterate

::: translit.transliterate

---

## slugify

::: translit.slugify

---

## normalize

::: translit.normalize

---

## normalize_confusables

::: translit.normalize_confusables

---

## sanitize_filename

::: translit.sanitize_filename

---

## strip_accents

::: translit.strip_accents

---

## fold_case

::: translit.fold_case

---

## collapse_whitespace

::: translit.collapse_whitespace

---

## demojize

::: translit.demojize

---

## set_emoji_provider

::: translit.set_emoji_provider

---

## strip_bidi

::: translit.strip_bidi

---

## strip_zalgo

::: translit.strip_zalgo

Caps the number of combining marks per base character, preserving legitimate diacritics (é, ñ, ệ) while removing zalgo stacking abuse.

```python
from translit import strip_zalgo

strip_zalgo("café")           # => "café"  (1 mark — preserved)
strip_zalgo("Việt Nam")       # => "Việt Nam"  (2 marks — preserved)

# Strip all combining marks (like strip_accents)
strip_zalgo("café", max_marks=0)  # => "cafe"
```

---

## List input (batch processing)

`transliterate`, `slugify`, `normalize`, and `strip_accents` accept either a single `str` or a `list[str]`. When a list is passed, all strings are processed in a single Rust call, amortizing the Python → Rust boundary overhead. The return type matches the input type.

```python
from translit import transliterate, slugify

titles = ["café résumé", "Straße nach München", "Москва"]

transliterate(titles)
# => ["cafe resume", "Strasse nach Munchen", "Moskva"]

slugify(titles, lang="de")
# => ["cafe-resume", "strasse-nach-muenchen", "moskva"]
```

For large datasets, passing a list is significantly faster than calling the function in a Python loop. See [Performance](../performance.md) for benchmarks.

## Compatibility aliases

The following aliases are provided for migration convenience:

| Alias | Target | Matches |
|---|---|---|
| `unidecode` | `transliterate` | Unidecode / text-unidecode |
| `ascii_fold` | `transliterate` | Elasticsearch ICU folding |
| `casefold` | `fold_case` | `str.casefold()` |
| `remove_accents` | `strip_accents` | sklearn / ML ecosystems |

```python
from translit import unidecode, casefold, remove_accents

unidecode("café")        # => "cafe"
casefold("Straße")       # => "strasse"
remove_accents("café")   # => "cafe"
```
