"""Tests for strip_obfuscation() preset pipeline.

strip_obfuscation is the most aggressive text normalization preset:
NFKC → strip_zalgo(max_marks=0) → strip_bidi → strip_zero_width
     → demojize → transliterate → confusables → strip_accents
     → fold_case → collapse_whitespace
"""

from __future__ import annotations

from translit import strip_obfuscation


class TestStripObfuscationBasic:
    """Core behavior: everything normalized to clean lowercase ASCII."""

    def test_cyrillic_text(self):
        result = strip_obfuscation("Москва лучший город")
        assert result.isascii()
        assert "moskva" in result

    def test_emoji_expanded(self):
        result = strip_obfuscation("hello 🔥 world")
        assert "fire" in result
        assert result.isascii()

    def test_adjacent_emoji_spaced(self):
        result = strip_obfuscation("🔥🔥🔥")
        assert "firefire" not in result
        parts = result.strip().split()
        assert parts.count("fire") == 3

    def test_mixed_cyrillic_emoji(self):
        result = strip_obfuscation("Москва ❤️ лучший город!")
        assert result.isascii()
        assert "moskva" in result


class TestStripObfuscationHomoglyphs:
    """Confusable homoglyphs must be neutralized."""

    def test_cyrillic_homoglyphs_in_latin(self):
        # Cyrillic а (U+0430) and е (U+0435) look like Latin a and e
        result = strip_obfuscation("p\u0430yp\u0430l is fr\u0435e")
        assert result == "paypal is free"

    def test_mixed_script_attack(self):
        # Greek Η (Eta) transliterates to "I" in modern Greek (BGN/PCGN),
        # not "H" — transliterate runs before confusables in this pipeline
        result = strip_obfuscation("Ηello")  # Greek Η + Latin ello
        assert result == "iello"


class TestStripObfuscationZalgo:
    """Zalgo/combining mark abuse must be fully stripped."""

    def test_zalgo_text(self):
        result = strip_obfuscation("H\u0300\u0301\u0302\u0303a\u0300\u0301\u0302\u0303te")
        # All combining marks stripped, then lowercased
        assert result == "hate"

    def test_strikethrough_text(self):
        result = strip_obfuscation("H\u0338a\u0338t\u0338e\u0338 speech")
        assert result == "hate speech"


class TestStripObfuscationInvisibleChars:
    """Zero-width and bidi characters must be removed."""

    def test_zero_width_space(self):
        result = strip_obfuscation("hello\u200bworld")
        assert result == "helloworld"

    def test_bidi_override(self):
        result = strip_obfuscation("admin\u202euser")
        assert result == "adminuser"

    def test_zero_width_joiner(self):
        result = strip_obfuscation("pass\u200dword")
        assert result == "password"


class TestStripObfuscationAccentsAndCase:
    """Accents stripped and case folded."""

    def test_accented_text(self):
        result = strip_obfuscation("Café Résumé")
        assert result == "cafe resume"

    def test_uppercase_folded(self):
        result = strip_obfuscation("HELLO WORLD")
        assert result == "hello world"

    def test_german_with_lang_default(self):
        # Without lang=, ü→u (default table), not ü→ue (German override)
        result = strip_obfuscation("München")
        assert result == "munchen"


class TestStripObfuscationWhitespace:
    """Whitespace collapsed, control chars stripped."""

    def test_multiple_spaces(self):
        result = strip_obfuscation("hello   world")
        assert result == "hello world"

    def test_control_chars(self):
        result = strip_obfuscation("hello\x00\x01world")
        assert "\x00" not in result
        assert "\x01" not in result

    def test_leading_trailing_stripped(self):
        result = strip_obfuscation("  hello  ")
        assert result == "hello"


class TestStripObfuscationEdgeCases:
    """Edge cases."""

    def test_empty_string(self):
        assert strip_obfuscation("") == ""

    def test_pure_ascii(self):
        assert strip_obfuscation("hello world") == "hello world"

    def test_already_clean(self):
        assert strip_obfuscation("clean text here") == "clean text here"
