# Encoding Detection & Decoding

Functions for detecting and converting byte sequences to UTF-8. Uses the chardetng algorithm (Firefox's encoding detector) for auto-detection.

## detect_encoding

::: translit.detect_encoding

```python
from translit import detect_encoding

enc, confidence = detect_encoding(b"Hello World")
# enc = "UTF-8", confidence ≈ 1.0

# Windows-1252 encoded text
enc, confidence = detect_encoding("café".encode("windows-1252"))
# enc = "windows-1252", confidence ≈ 0.87
```

!!! warning
    Automatic encoding detection is inherently probabilistic. A high confidence score does not guarantee correctness. For critical pipelines, always prefer explicit encoding metadata (HTTP headers, BOM, schema definitions) over detection.

---

## decode_to_utf8

::: translit.decode_to_utf8

```python
from translit import decode_to_utf8

# Explicit encoding
text, had_errors = decode_to_utf8(b"caf\xe9", "windows-1252")
# text = "café", had_errors = False

# Auto-detection
text, had_errors = decode_to_utf8(raw_bytes)

# Require high confidence for auto-detection
text, had_errors = decode_to_utf8(raw_bytes, min_confidence=0.8)
# Raises TranslitError if detected confidence < 0.8
```

Supports all WHATWG encodings: UTF-8, windows-1252, ISO-8859-1, Shift_JIS, EUC-JP, EUC-KR, Big5, GB18030, and more.
