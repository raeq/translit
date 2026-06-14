//! PyO3 shims for `crate::encoding` (Layer-1).
//!
//! Take Python `bytes`; `_decode_to_utf8` converts the native [`crate::Error`]
//! (unknown/low-confidence encoding, out-of-range threshold, strict lossy decode)
//! to a Python exception via `?`.

use pyo3::prelude::*;
use pyo3::types::PyBytes;

/// `detect_encoding(data) -> tuple[str, float]`
#[pyfunction]
#[pyo3(signature = (data,))]
pub fn _detect_encoding(data: &Bound<'_, PyBytes>) -> (String, f64) {
    crate::encoding::detect_encoding_impl(data.as_bytes())
}

/// `decode_to_utf8(data, encoding=None, min_confidence=0.95, strict=False) -> tuple[str, bool]`
#[pyfunction]
#[pyo3(signature = (data, encoding = None, min_confidence = 0.95, strict = false))]
pub fn _decode_to_utf8(
    data: &Bound<'_, PyBytes>,
    encoding: Option<&str>,
    min_confidence: f64,
    strict: bool,
) -> PyResult<(String, bool)> {
    Ok(crate::encoding::decode_to_utf8_impl(
        data.as_bytes(),
        encoding,
        min_confidence,
        strict,
    )?)
}
