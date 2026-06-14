//! Minimal pure-Rust quickstart for the `disarm` crate (#42).
//!
//! Builds and runs against the default (pyo3-free) feature set — the same code a
//! crates.io consumer writes after `cargo add disarm`. No Python, no libpython.
//!
//! Run with: `cargo run --example rust_quickstart`

use disarm::{api, ErrorMode};

fn main() {
    // TR39 confusable folding (Cyrillic look-alikes → Latin prototypes).
    assert_eq!(
        api::normalize_confusables("раypal", api::TargetScript::Latin),
        "paypal"
    );

    // Standards-based transliteration to ASCII (infallible; ASCII passes through).
    let moscow = api::transliterate("Москва", None, ErrorMode::Replace, "?", false, false, false);
    assert_eq!(moscow, "Moskva");

    // Canonicalization primitives.
    assert_eq!(api::strip_accents("café"), "cafe");
    assert_eq!(api::fold_case("ﬁ"), "fi");
    assert_eq!(
        api::slugify("Héllo Wörld", &api::SlugConfig::default()),
        "hello-world"
    );

    // IDN / hostname spoofing check (a `false` result is not a safety guarantee).
    let (suspicious, _analysis) = api::is_suspicious_hostname("раypal.com");
    assert!(suspicious);

    // Fallible surface: an unknown encoding label is rejected with a stable kind.
    let err = api::decode_to_utf8(b"x", Some("NO-SUCH-ENCODING"), 0.0, false).unwrap_err();
    assert_eq!(err.kind(), disarm::ErrorKind::InvalidArgument);

    println!("disarm pure-Rust quickstart: all assertions passed ✓");
}
