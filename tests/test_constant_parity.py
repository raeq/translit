"""#200: guard against silent drift between the Python wrapper's mirror
constants and the Rust constants / enum strings they reflect.

- ``_MAX_BATCH_SIZE`` is now imported from the Rust extension (single source of
  truth); these tests pin that wiring so a future edit cannot quietly re-declare
  a diverging literal.
- The error-mode / norm-form string sets are validated against Rust's *actual*
  acceptance (a round-trip), so if Rust ever drops support for one the Python
  list still claims, this fails here rather than silently.
"""

from __future__ import annotations

import pytest

import translit
from translit import _api
from translit._translit import _MAX_BATCH_SIZE as _RUST_MAX_BATCH_SIZE


class TestResourceLimitParity:
    def test_max_batch_size_sourced_from_rust(self) -> None:
        # The wrapper must read the Rust value, not a re-declared literal.
        assert _api._MAX_BATCH_SIZE == _RUST_MAX_BATCH_SIZE
        assert _api._MAX_BATCH_SIZE > 0

    def test_batch_guard_reports_the_rust_limit(self) -> None:
        over = ["x"] * (_api._MAX_BATCH_SIZE + 1)
        with pytest.raises((translit.TranslitError, ValueError)) as exc:
            translit.transliterate(over)
        assert str(_api._MAX_BATCH_SIZE) in str(exc.value)


class TestEnumStringParity:
    def test_every_declared_error_mode_accepted_by_rust(self) -> None:
        # Non-ASCII input reaches the Rust transliteration path for each mode.
        for mode in _api._VALID_ERROR_MODES:
            translit.transliterate("é", errors=mode)

    def test_bogus_error_mode_rejected(self) -> None:
        with pytest.raises((translit.TranslitError, ValueError)):
            translit.transliterate("é", errors="bogus")  # type: ignore[arg-type]

    def test_every_declared_norm_form_accepted_by_rust(self) -> None:
        for form in _api._VALID_NORM_FORMS:
            translit.normalize("é", form=form)

    def test_bogus_norm_form_rejected(self) -> None:
        with pytest.raises((translit.TranslitError, ValueError)):
            translit.normalize("é", form="BOGUS")  # type: ignore[arg-type]
