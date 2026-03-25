# Contributing to translit

Thank you for your interest in contributing!

## Prerequisites

- Rust stable toolchain (>= 1.70): `rustup update stable`
- Python 3.9+
- `maturin` for building the Python extension: `pip install maturin[patchelf]`

## Development setup

```bash
git clone https://github.com/raeq/translit.git
cd translit
python -m venv .venv && source .venv/bin/activate
maturin develop          # build Rust extension in-place
pip install -e ".[dev]"  # installs test + dev dependencies
pre-commit install       # set up pre-commit hooks
```

## Running tests

```bash
# Python tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=translit --cov-report=term-missing

# Including type checks (requires Python 3.10+)
pytest tests/test_typing.py -v

# Rust tests
cargo test --no-default-features

# Doctests
pytest --doctest-modules python/translit/__init__.py python/translit/_compat.py
```

## Linting and formatting

```bash
# Rust
cargo fmt --check
cargo clippy --no-default-features -- -D warnings

# Python
ruff check python/ tests/
ruff format --check python/ tests/
mypy python/translit/__init__.py --ignore-missing-imports
```

## Building documentation

```bash
pip install -e ".[docs]"
mkdocs serve              # local preview at http://127.0.0.1:8000
mkdocs build              # build static site to site/
```

## Submitting changes

1. Fork the repository and create a branch from `main`.
2. Make your changes with tests.
3. Ensure all CI checks pass locally.
4. Open a pull request with a clear description of what changed and why.

## Reporting bugs

Please open an issue at https://github.com/raeq/translit/issues with:
- A minimal reproducing example
- Expected vs actual output
- Python and OS version
