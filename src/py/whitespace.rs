//! PyO3 shim for `crate::whitespace` (Layer-1). Infallible.

use pyo3::prelude::*;

/// `collapse_whitespace(text, *, strip_control=True, strip_zero_width=True) -> str`
#[pyfunction]
#[pyo3(signature = (text, *, strip_control = true, strip_zero_width = true))]
pub fn _collapse_whitespace(text: &str, strip_control: bool, strip_zero_width: bool) -> String {
    crate::whitespace::collapse_whitespace(text, strip_control, strip_zero_width)
}
