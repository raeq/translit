//! Layer 2: the idiomatic, pyo3-free Rust API — the future crates.io surface (#38).
//!
//! These wrap the Layer-1 algorithm modules with typed parameters and infallible
//! signatures where the type system already rules out the error. The PyO3 shims
//! (`src/py/`) and the planned C-ABI consume the same Layer-1 core, so this is
//! the one place the public Rust behaviour is defined.
//!
//! This module is built up incrementally (sub-PR by sub-PR) as each algorithm
//! module is migrated to the Layer-1/Layer-2/Layer-3 split; `confusables` was the
//! first, landing the canonical template.

// ── Confusables (TR39) ──────────────────────────────────────────────────────

/// Target script for confusable folding (see [`normalize_confusables`]).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum TargetScript {
    /// Fold confusables onto their Latin prototypes (the common case).
    Latin,
    /// Fold confusables onto their Cyrillic prototypes.
    Cyrillic,
}

impl TargetScript {
    /// The lowercase token the underlying tables are keyed by.
    fn as_str(self) -> &'static str {
        match self {
            TargetScript::Latin => "latin",
            TargetScript::Cyrillic => "cyrillic",
        }
    }
}

/// Replace Unicode confusable homoglyphs with their `target`-script prototypes
/// (TR39). Characters with no mapping pass through unchanged.
///
/// Infallible: a [`TargetScript`] is always a supported script.
pub fn normalize_confusables(text: &str, target: TargetScript) -> String {
    // The only error path of the Layer-1 fn is an unsupported target *string*;
    // a `TargetScript` value can never produce one, so this is unreachable.
    crate::confusables::normalize_confusables(text, target.as_str())
        .expect("TargetScript always maps to a supported target script")
}

/// True if `text` contains any character confusable with a `target`-script
/// character (TR39).
///
/// Infallible: a [`TargetScript`] is always a supported script.
pub fn is_confusable(text: &str, target: TargetScript) -> bool {
    crate::confusables::is_confusable(text, target.as_str())
        .expect("TargetScript always maps to a supported target script")
}

// ── Terminal width (UAX #11 / UAX #29) ───────────────────────────────────────

/// Total terminal column width of `text`, summed over UAX #29 grapheme clusters
/// (#224). Measures cells, not pixels; does not expand tabs or model wrapping.
///
/// `ambiguous_wide` selects the East-Asian Ambiguous policy (UAX #11): when
/// `true`, ambiguous-width characters count as 2 cells, otherwise 1.
pub fn terminal_width(text: &str, ambiguous_wide: bool) -> usize {
    crate::width::terminal_width_opts(text, ambiguous_wide)
}

/// Column width of a single grapheme cluster (see [`terminal_width`]).
///
/// `ambiguous_wide` selects the East-Asian Ambiguous policy (UAX #11): when
/// `true`, ambiguous-width characters count as 2 cells, otherwise 1.
pub fn grapheme_width(cluster: &str, ambiguous_wide: bool) -> usize {
    crate::width::grapheme_width_opts(cluster, ambiguous_wide)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalize_folds_cyrillic_to_latin() {
        // Cyrillic 'а' (U+0430) → Latin 'a'.
        assert_eq!(
            normalize_confusables("\u{0430}pple", TargetScript::Latin),
            "apple"
        );
        assert_eq!(normalize_confusables("hello", TargetScript::Latin), "hello");
        assert_eq!(normalize_confusables("", TargetScript::Latin), "");
    }

    #[test]
    fn is_confusable_detects_homoglyph() {
        assert!(is_confusable("p\u{0430}ypal", TargetScript::Latin)); // Cyrillic 'а'
        assert!(!is_confusable("paypal", TargetScript::Latin));
    }

    #[test]
    fn target_script_tokens() {
        assert_eq!(TargetScript::Latin.as_str(), "latin");
        assert_eq!(TargetScript::Cyrillic.as_str(), "cyrillic");
    }

    #[test]
    fn terminal_width_sums_clusters() {
        assert_eq!(terminal_width("hello", false), 5);
        assert_eq!(terminal_width("世界", false), 4); // wide CJK
        assert_eq!(terminal_width("", false), 0);
    }

    #[test]
    fn grapheme_width_single_cluster() {
        assert_eq!(grapheme_width("a", false), 1);
        assert_eq!(grapheme_width("世", false), 2);
        assert_eq!(grapheme_width("👨\u{200D}👩\u{200D}👧\u{200D}👦", false), 2);
        // ZWJ family
    }

    #[test]
    fn ambiguous_wide_policy() {
        // U+00A1 INVERTED EXCLAMATION MARK is East Asian Ambiguous.
        assert_eq!(terminal_width("\u{00A1}", false), 1);
        assert_eq!(terminal_width("\u{00A1}", true), 2);
        assert_eq!(grapheme_width("\u{00A1}", true), 2);
    }
}
