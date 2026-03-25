# Stage 1: Build the wheel from source
FROM python:3.12-slim AS build

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.cargo/bin:$PATH"

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir maturin

COPY Cargo.toml build.rs pyproject.toml README.md ./
COPY src/ src/
COPY python/ python/

RUN cargo generate-lockfile && \
    maturin build --release --interpreter python --out /tmp/wheels && \
    pip install --no-cache-dir /tmp/wheels/*.whl

# Stage 2: Minimal runtime image
FROM python:3.12-slim

# Create non-root user
RUN groupadd --gid 1000 translit && \
    useradd --uid 1000 --gid translit --no-create-home translit

# Copy venv from build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

USER translit

ENTRYPOINT ["python", "-m", "translit"]
