//! PyO3 shim for `crate::log_injection` (Layer-1).
//!
//! Validates `replacement` at the boundary (the native [`crate::Error`] converts
//! via `?`), then returns the original `PyString` object zero-copy for a clean
//! line (#307).

use std::borrow::Cow;

use pyo3::prelude::*;
use pyo3::types::PyString;

/// `strip_log_injection(text, *, replacement, keep_tab) -> str`
// No defaults in the FFI signature: the Python wrapper supplies them. (A
// non-ASCII default like U+FFFD in `__text_signature__` is unparseable by
// `inspect.signature`, which the stub-drift test relies on.)
#[pyfunction]
#[pyo3(signature = (text, *, replacement, keep_tab))]
pub fn _strip_log_injection<'py>(
    text: &Bound<'py, PyString>,
    replacement: &str,
    keep_tab: bool,
) -> PyResult<Bound<'py, PyString>> {
    crate::log_injection::validate_log_replacement(replacement, keep_tab)?;
    let s = text.to_cow()?;
    match crate::log_injection::strip_log_injection_str(&s, replacement, keep_tab) {
        // Clean line → hand back the original object (refcount bump, no copy).
        Cow::Borrowed(_) => Ok(text.clone()),
        Cow::Owned(out) => Ok(PyString::new(text.py(), &out)),
    }
}
