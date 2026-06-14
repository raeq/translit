#![no_main]
//! Fuzz `normalize_confusables`: must never panic, and the output must
//! contain no character the bundled table still maps (a fixed point).
//!
//! Drives the public Layer-2 API (`_disarm::api`), which is infallible for a
//! typed `TargetScript`, so there is no error arm to guard.
use _disarm::api::{normalize_confusables, TargetScript};
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &str| {
    for target in [TargetScript::Latin, TargetScript::Cyrillic] {
        let once = normalize_confusables(data, target);
        let twice = normalize_confusables(&once, target);
        assert_eq!(
            once, twice,
            "normalize_confusables({target:?}) not idempotent on {data:?}"
        );
    }
});
