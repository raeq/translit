# Grapheme Clusters

Functions for working with user-perceived characters (extended grapheme clusters) as defined by UAX #29. These give correct results for emoji, combining characters, and complex scripts where Python's `len()` overcounts.

## grapheme_len

::: translit.grapheme_len

```python
from translit import grapheme_len

grapheme_len("café")                 # => 4
grapheme_len("👨‍👩‍👧‍👦")                    # => 1 (family emoji = 1 cluster)
grapheme_len("🇫🇷")                    # => 1 (flag = 1 cluster, but len() = 2)
grapheme_len("é")                    # => 1 (even if NFD: e + combining acute)
```

---

## grapheme_split

::: translit.grapheme_split

```python
from translit import grapheme_split

grapheme_split("café")               # => ['c', 'a', 'f', 'é']
grapheme_split("👨‍👩‍👧‍👦!")               # => ['👨‍👩‍👧‍👦', '!']
```

!!! note
    Input is limited to 10 MB to prevent excessive memory allocation. Raises `TranslitError` for larger inputs.

---

## grapheme_truncate

::: translit.grapheme_truncate

```python
from translit import grapheme_truncate

grapheme_truncate("Hello World", 5)  # => "Hello"
grapheme_truncate("café", 3)         # => "caf"
grapheme_truncate("👨‍👩‍👧‍👦🎉", 1)         # => "👨‍👩‍👧‍👦" (never splits a cluster)
```

Unlike byte-level or codepoint-level truncation, `grapheme_truncate` never splits a grapheme cluster, which would corrupt emoji, combining sequences, or Hangul syllables.
