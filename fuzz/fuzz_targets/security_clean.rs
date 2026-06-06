#![no_main]
//! Fuzz `security_clean`: must never panic on any input.
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &str| {
    let _ = _translit::presets::_security_clean(data);
});
