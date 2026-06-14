//! PyO3 shims for `crate::width` (Layer-1).
//!
//! Thin wrappers exposing `_terminal_width` / `_grapheme_width` to Python. Both
//! are infallible (width is a total function over text), so there is no error
//! conversion; all behaviour lives in the Layer-1 module.

use pyo3::prelude::*;

/// `terminal_width(text, *, ambiguous_wide=False) -> int`
#[pyfunction]
#[pyo3(signature = (text, *, ambiguous_wide = false))]
pub fn _terminal_width(text: &str, ambiguous_wide: bool) -> usize {
    crate::width::terminal_width_opts(text, ambiguous_wide)
}

/// `grapheme_width(cluster, *, ambiguous_wide=False) -> int`
#[pyfunction]
#[pyo3(signature = (cluster, *, ambiguous_wide = false))]
pub fn _grapheme_width(cluster: &str, ambiguous_wide: bool) -> usize {
    crate::width::grapheme_width_opts(cluster, ambiguous_wide)
}
