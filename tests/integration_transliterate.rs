//! Integration tests for the transliteration public API.
//!
//! These tests exercise the Rust API surface as an external consumer would,
//! complementing the inline unit tests in each module.

use _translit::transliterate;
use _translit::ErrorMode;

#[test]
fn ascii_passthrough() {
    let result =
        transliterate::transliterate_impl("hello world", None, ErrorMode::Ignore, "", false);
    assert_eq!(result, "hello world");
}

#[test]
fn latin_accented_to_ascii() {
    let result =
        transliterate::transliterate_impl("café résumé", None, ErrorMode::Ignore, "", false);
    assert!(result.is_ascii(), "expected ASCII, got: {result:?}");
    assert!(result.contains("cafe"), "expected 'cafe' in {result:?}");
    assert!(result.contains("resume"), "expected 'resume' in {result:?}");
}

#[test]
fn cyrillic_default_lang() {
    let result = transliterate::transliterate_impl("Москва", None, ErrorMode::Ignore, "", false);
    assert!(result.is_ascii());
    // Default transliteration should produce something recognizable
    assert!(!result.is_empty());
}

#[test]
fn cyrillic_with_lang() {
    let result =
        transliterate::transliterate_impl("Москва", Some("ru"), ErrorMode::Ignore, "", false);
    assert!(result.is_ascii());
    assert!(!result.is_empty());
}

#[test]
fn chinese_cjk() {
    let result = transliterate::transliterate_impl("中文", None, ErrorMode::Ignore, "", false);
    assert!(result.is_ascii());
}

#[test]
fn error_mode_preserve() {
    let result =
        transliterate::transliterate_impl("abc 日本語 xyz", None, ErrorMode::Preserve, "", false);
    assert!(result.contains("abc"));
    assert!(result.contains("xyz"));
}

#[test]
fn error_mode_replace() {
    let result = transliterate::transliterate_impl("café", None, ErrorMode::Replace, "?", false);
    assert!(result.is_ascii());
}

#[test]
fn strip_accents_basic() {
    assert_eq!(transliterate::_strip_accents("café"), "cafe");
    assert_eq!(transliterate::_strip_accents("naïve"), "naive");
    assert_eq!(transliterate::_strip_accents("über"), "uber");
}

#[test]
fn strip_accents_passthrough() {
    assert_eq!(transliterate::_strip_accents("hello"), "hello");
    assert_eq!(transliterate::_strip_accents(""), "");
}

#[test]
fn is_ascii_check() {
    assert!(transliterate::_is_ascii("hello"));
    assert!(!transliterate::_is_ascii("café"));
    assert!(transliterate::_is_ascii(""));
}

#[test]
fn list_langs_contains_common() {
    let langs = transliterate::_list_langs();
    // Should have some built-in language tables
    assert!(!langs.is_empty());
}

#[test]
fn idempotent_transliteration() {
    let input = "Héllo Wörld café";
    let once = transliterate::transliterate_impl(input, None, ErrorMode::Ignore, "", false);
    let twice = transliterate::transliterate_impl(&once, None, ErrorMode::Ignore, "", false);
    assert_eq!(once, twice, "transliteration should be idempotent");
}

#[test]
fn empty_input() {
    let result = transliterate::transliterate_impl("", None, ErrorMode::Ignore, "", false);
    assert_eq!(result, "");
}

#[test]
fn strict_iso9_cyrillic() {
    let result = transliterate::transliterate_impl("Москва", None, ErrorMode::Ignore, "", true);
    assert!(result.is_ascii());
}
