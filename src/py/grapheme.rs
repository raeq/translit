//! PyO3 shims for `crate::grapheme` (Layer-1).
//!
//! `_grapheme_len` / `_grapheme_split` are infallible; `_grapheme_truncate`
//! validates the non-negative `max_graphemes` contract here at the boundary
//! (#231) — Layer 1 / Layer 2 take an already-checked `usize`.

use pyo3::prelude::*;

/// `grapheme_len(text) -> int`
#[pyfunction]
#[pyo3(signature = (text,))]
pub fn _grapheme_len(text: &str) -> usize {
    crate::grapheme::grapheme_len(text)
}

/// `grapheme_split(text) -> list[str]`
#[pyfunction]
#[pyo3(signature = (text,))]
pub fn _grapheme_split(text: &str) -> Vec<String> {
    crate::grapheme::grapheme_split(text)
}

/// `grapheme_truncate(text, max_graphemes) -> str`
#[pyfunction]
#[pyo3(signature = (text, max_graphemes))]
pub fn _grapheme_truncate(text: &str, max_graphemes: i64) -> PyResult<String> {
    let max_graphemes = crate::error::checked_max_graphemes(max_graphemes)?;
    Ok(crate::grapheme::truncate_to_graphemes(text, max_graphemes))
}
