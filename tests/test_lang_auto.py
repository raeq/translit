"""Tests for lang='auto' script-based language detection."""

import pytest

from translit import Slugifier, TextPipeline, slugify, transliterate


class TestLangAutoDetection:
    """lang='auto' detects script and uses appropriate language table."""

    @pytest.mark.parametrize(
        "text,expected_lang",
        [
            ("ภาษาไทย", "th"),
            ("Москва", "ru"),
            ("नमस्ते", "hi"),
            ("こんにちは", "ja"),
            ("中文", "zh"),
            ("한국어", "ko"),
            ("עברית", "he"),
            ("العربية", "ar"),
            ("ქართული", "ka"),
            ("Հայերեն", "hy"),
            ("ትግርኛ", "am"),
            ("বাংলা", "bn"),
            ("தமிழ்", "ta"),
            ("తెలుగు", "te"),
            ("ಕನ್ನಡ", "kn"),
            ("മലയാളം", "ml"),
            ("ગુજરાતી", "gu"),
            ("ਗੁਰਮੁਖੀ", "pa"),
            ("ଓଡ଼ିଆ", "or"),
            ("සිංහල", "si"),
            ("ພາສາລາວ", "lo"),
            ("မြန်မာ", "my"),
            ("ភាសាខ្មែរ", "km"),
            ("བོད་སྐད", "bo"),
            ("Ελληνικά", "el"),
        ],
    )
    def test_auto_matches_explicit_lang(self, text: str, expected_lang: str) -> None:
        auto = transliterate(text, lang="auto")
        explicit = transliterate(text, lang=expected_lang)
        assert auto == explicit

    def test_auto_ascii_passthrough(self) -> None:
        assert transliterate("hello", lang="auto") == "hello"

    def test_auto_latin_accented_uses_default(self) -> None:
        assert transliterate("café", lang="auto") == transliterate("café")

    def test_auto_mixed_latin_cyrillic(self) -> None:
        """First non-Latin script wins."""
        result = transliterate("Hello Москва", lang="auto")
        expected = transliterate("Hello Москва", lang="ru")
        assert result == expected

    def test_slugify_auto(self) -> None:
        result = slugify("ภาษาไทย", lang="auto")
        expected = slugify("ภาษาไทย", lang="th")
        assert result == expected

    def test_pipeline_auto(self) -> None:
        p = TextPipeline(transliterate=True, lang="auto")
        result = p("Москва")
        assert result.isascii()

    def test_slugifier_auto(self) -> None:
        s = Slugifier(lang="auto")
        result = s("東京タワー")
        assert result.isascii()
        assert len(result) > 0
