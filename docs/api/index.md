# API Reference

Complete reference for all public functions, classes, and types in translit.

## Modules

| Module | Description |
|---|---|
| [Core Transforms](transforms.md) | Text transformation functions |
| [Precompiled Pipelines](pipelines.md) | Ready-to-use multi-step pipelines |
| [Predicates](predicates.md) | Text inspection functions |
| [Grapheme Clusters](graphemes.md) | User-perceived character operations |
| [Encoding](encoding.md) | Byte sequence detection and decoding |
| [Classes](classes.md) | Text, Slugifier, UniqueSlugifier, TextPipeline |
| [Enums & Types](enums.md) | Script, NF, EmojiProvider, type aliases |
| [Language Profiles](language-profiles.md) | Language listing and registration |
| [Exceptions](exceptions.md) | TranslitError |

## Import convention

All public symbols are available from the top-level package:

```python
from translit import transliterate, slugify, Script, LANG_DE
```

Domain-specific namespaces are also available:

```python
from translit.security import is_confusable, security_clean
from translit.normalization import fold_case, strip_accents
from translit.codec import decode_to_utf8, detect_encoding
from translit.files import sanitize_filename
```

## Compatibility aliases

translit provides drop-in aliases for several legacy libraries:

```python
# Unidecode / text-unidecode
from translit import unidecode

# str.casefold() / sklearn
from translit import casefold, remove_accents

# awesome-slugify
from translit import Slugify, UniqueSlugify
from translit import slugify_url, slugify_filename, slugify_unicode
from translit import slugify_ru, slugify_de, slugify_el

# Elasticsearch/Solr
from translit import ascii_fold
```

See [Classes → Compatibility aliases](classes.md#compatibility-aliases-awesome-slugify) and the [migration guides](../migration/index.md) for details.

## Type annotations

translit is fully typed. A `py.typed` marker file and `.pyi` stub files are included for mypy and pyright support.

```python
# All functions have full type annotations
reveal_type(transliterate("test"))  # str
reveal_type(detect_scripts("test")) # list[Script]
reveal_type(is_ascii("test"))       # bool
```
