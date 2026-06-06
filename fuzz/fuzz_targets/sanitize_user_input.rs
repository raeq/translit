#![no_main]
//! Fuzz `sanitize_user_input`: must never panic on any input.
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &str| {
    let _ = _translit::presets::_sanitize_user_input(data);
});
