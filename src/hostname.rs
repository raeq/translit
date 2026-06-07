use pyo3::prelude::*;
use unicode_normalization::UnicodeNormalization;

use crate::{confusables, scripts};

/// Check if a bracketed string is a valid IPv6 literal per RFC 3986 §3.2.2.
///
/// Requires: starts with `[`, ends with `]`, content contains `:`,
/// only hex digits / colons / dots / `%` (zone ID), and no more than 7 colons.
fn is_ipv6_literal(normalized: &str) -> bool {
    if !(normalized.starts_with('[') && normalized.ends_with(']')) {
        return false;
    }
    let inner = &normalized[1..normalized.len() - 1];
    if inner.is_empty() || !inner.contains(':') {
        return false;
    }
    // Validate colon count on the address portion (before any zone ID).
    let addr_part = match inner.find('%') {
        Some(pos) => &inner[..pos],
        None => inner,
    };
    let colon_count = addr_part.chars().filter(|&c| c == ':').count();
    if colon_count > 7 {
        return false;
    }
    inner
        .as_bytes()
        .iter()
        .all(|&b| b.is_ascii_hexdigit() || b == b':' || b == b'.' || b == b'%')
}

/// Check if a hostname is safe from Unicode homoglyph attacks.
///
/// `xn--` (ACE) labels are decoded to their Unicode form via UTS#46 before
/// analysis, so the on-the-wire IDN homograph attack is examined rather than
/// passed through as inert ASCII (#63). A malformed ACE label is treated as
/// unsafe (fail closed).
///
/// A hostname is considered unsafe if:
/// - It contains characters from multiple scripts (mixed-script)
///   AND at least one script pair is high-risk (Cyrillic+Latin, Greek+Latin)
/// - It contains confusable characters that map to different Latin characters
/// - An ACE label fails to decode, or a confusable check errors (fail closed)
///
/// Returns a tuple of (is_safe, details) where details is a dict with:
/// - "safe": bool
/// - "scripts": list of detected scripts
/// - "mixed_script": bool
/// - "has_confusables": bool
/// - "canonical": the Latin-normalized form
///
/// This is a conservative check — it flags anything suspicious rather than
/// trying to determine benign intent.
#[pyfunction]
#[pyo3(signature = (hostname,))]
pub fn _is_safe_hostname(hostname: &str) -> PyResult<(bool, SafeHostnameDetails)> {
    // 1. NFKC normalize
    let normalized: String = hostname.nfkc().collect();

    // IPv6 literals (e.g. "[::1]", "[2001:db8::1]") are not IDN hostnames and
    // cannot be visually spoofed via homoglyph attacks. Return them as safe
    // without running the script/confusable analysis.
    if is_ipv6_literal(&normalized) {
        return Ok((
            true,
            SafeHostnameDetails {
                safe: true,
                scripts: Vec::new(),
                mixed_script: false,
                has_confusables: false,
                canonical: normalized,
            },
        ));
    }

    // 2. Split on dots to check each label
    let mut overall_safe = true;
    let mut all_scripts: Vec<&str> = Vec::new();
    let mut seen_scripts: std::collections::HashSet<&str> = std::collections::HashSet::new();
    let mut has_mixed = false;
    let mut has_confusables = false;
    let mut decoded_labels: Vec<String> = Vec::new();

    for raw_label in normalized.split('.') {
        // Empty labels arise from leading, trailing, or consecutive dots
        // (e.g. "a..b" or "example.com.").  These are structurally
        // malformed but not a homoglyph attack vector — skip them (but keep a
        // placeholder so the canonical form preserves dot structure).
        if raw_label.is_empty() {
            decoded_labels.push(String::new());
            continue;
        }

        // Decode `xn--` ACE labels to their Unicode form (UTS#46, #63) so the
        // on-the-wire IDN homograph attack is analysed instead of passing as
        // inert ASCII. A malformed ACE label cannot be verified → fail closed.
        // Byte comparison (not `raw_label[..4]`, which would panic on a
        // non-ASCII label where byte 4 is not a char boundary). ACE labels are
        // pure ASCII, so a byte-prefix match is exactly right. `>= 4` (not
        // `> 4`) so a bare, malformed `"xn--"` is still recognised as ACE and
        // routed through the fail-closed decode below rather than slipping past
        // as an inert ASCII label.
        let is_ace =
            raw_label.len() >= 4 && raw_label.as_bytes()[..4].eq_ignore_ascii_case(b"xn--");
        let label: String = if is_ace {
            let (unicode, result) = idna::domain_to_unicode(raw_label);
            if result.is_err() {
                overall_safe = false;
            }
            unicode.nfkc().collect()
        } else {
            raw_label.to_string()
        };
        decoded_labels.push(label.clone());

        // Check scripts in this (decoded) label
        let label_scripts = scripts::_detect_scripts(&label);

        // Track all scripts seen (O(1) dedup via HashSet)
        for s in &label_scripts {
            if seen_scripts.insert(s) {
                all_scripts.push(s);
            }
        }

        // Mixed-script within a single label is suspicious
        if label_scripts.len() > 1 {
            const HIGH_RISK_PAIRS: &[(&str, &str)] = &[
                ("Cyrillic", "Latin"),
                ("Greek", "Latin"),
                ("Armenian", "Latin"),
                ("Cherokee", "Latin"),
            ];

            has_mixed = true;

            // High-risk script combinations (visually confusable with Latin).
            let script_set: std::collections::HashSet<&str> =
                label_scripts.iter().copied().collect();

            for &(a, b) in HIGH_RISK_PAIRS {
                if script_set.contains(a) && script_set.contains(b) {
                    overall_safe = false;
                }
            }
        }

        // Check confusables in this label. Fail CLOSED (#67.1): if the check
        // errors we cannot prove the label safe, so treat it as unsafe rather
        // than silently degrading to "not confusable".
        match confusables::_is_confusable(&label, "latin") {
            Ok(true) => {
                has_confusables = true;
                overall_safe = false;
            }
            Ok(false) => {}
            Err(_) => {
                overall_safe = false;
            }
        }
    }

    // Generate canonical Latin form from the decoded labels.
    let decoded_hostname = decoded_labels.join(".");
    let canonical =
        confusables::_normalize_confusables(&decoded_hostname, "latin").unwrap_or(decoded_hostname);

    Ok((
        overall_safe,
        SafeHostnameDetails {
            safe: overall_safe,
            scripts: all_scripts.into_iter().map(String::from).collect(),
            mixed_script: has_mixed,
            has_confusables,
            canonical,
        },
    ))
}

/// Details from hostname safety check.
#[pyclass]
#[pyo3(name = "SafeHostnameDetails")]
#[derive(Clone)]
pub struct SafeHostnameDetails {
    #[pyo3(get)]
    pub safe: bool,
    #[pyo3(get)]
    pub scripts: Vec<String>,
    #[pyo3(get)]
    pub mixed_script: bool,
    #[pyo3(get)]
    pub has_confusables: bool,
    #[pyo3(get)]
    pub canonical: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_safe_hostname() {
        let (safe, details) = _is_safe_hostname("paypal.com").unwrap();
        assert!(safe);
        assert!(!details.has_confusables);
        assert!(!details.mixed_script);
    }

    #[test]
    fn test_cyrillic_spoof() {
        // Cyrillic а and р mixed with Latin
        let (safe, details) = _is_safe_hostname("\u{0440}\u{0430}ypal.com").unwrap();
        assert!(!safe);
        assert!(details.has_confusables);
        assert!(details.mixed_script);
        assert_eq!(details.canonical, "paypal.com");
    }

    #[test]
    fn test_full_cyrillic_domain() {
        // Fully Cyrillic domain — not mixed script, might have confusables
        let (_, details) = _is_safe_hostname("яндекс.ру").unwrap();
        assert!(!details.mixed_script);
    }

    #[test]
    fn test_punycode_non_homograph_safe() {
        // xn--n3h.com decodes to ☃.com (a snowman) — a single-script non-Latin
        // label, not a homoglyph spoof, so it is correctly reported safe. The
        // point of #63 is that the label is now *decoded and analysed*, not that
        // every xn-- label is flagged.
        let (safe, _) = _is_safe_hostname("xn--n3h.com").unwrap();
        assert!(safe);
    }

    #[test]
    fn test_punycode_homograph_unsafe() {
        // #63: the on-the-wire ACE form of a Cyrillic homograph must be decoded
        // and flagged. Build the xn-- form of a Cyrillic "apple" spoof, then
        // assert _is_safe_hostname rejects it (it used to pass as safe ASCII).
        let spoof = "\u{0430}\u{0440}\u{0440}\u{04CF}\u{0435}"; // аррӏе (Cyrillic)
        let ace = idna::domain_to_ascii(spoof).expect("encode Cyrillic spoof to ACE");
        assert!(
            ace.starts_with("xn--"),
            "expected an xn-- label, got {ace:?}"
        );
        let hostname = format!("{ace}.com");
        let (safe, details) = _is_safe_hostname(&hostname).unwrap();
        assert!(
            !safe,
            "Cyrillic homograph in ACE form {hostname:?} must be unsafe"
        );
        assert!(details.has_confusables);
    }

    #[test]
    fn test_ipv6_loopback_safe() {
        let (safe, details) = _is_safe_hostname("[::1]").unwrap();
        assert!(safe);
        assert!(!details.mixed_script);
        assert!(!details.has_confusables);
    }

    #[test]
    fn test_ipv6_full_safe() {
        let (safe, details) = _is_safe_hostname("[2001:db8::1]").unwrap();
        assert!(safe);
        assert!(details.scripts.is_empty());
    }
}
