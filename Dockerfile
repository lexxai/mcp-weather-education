ARG PYTHON_VERSION=3.14
ARG UV_PYTHON=${UV_PYTHON:-}

ARG PYTHON_BUILDER=python:${PYTHON_VERSION}
ARG PYTHON_BUILDER_SLIM=python:${PYTHON_VERSION}-slim

ARG PYTHON_REPO=${PYTHON_APP:-$PYTHON_BUILDER_SLIM}

ARG REPO_BUILD=${REPO_BUILDER:-$PYTHON_BUILDER}
ARG REPO=${PYTHON_REPO:-$REPO_BUILD}

ARG PYTHONPATH=${PYTHONPATH:-}

FROM ${REPO_BUILD} AS builder

ARG UV_PYTHON

# Install uv
# RUN pip install uv
# Use an official image to get the uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set work directory
WORKDIR /app

# Install dependencies
COPY "pyproject.toml" "uv.lock" ./
ENV UV_PYTHON=${UV_PYTHON}
#--locked
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked;

FROM ${REPO}

ARG _USER=appuser
ARG _GROUP=appgroup
ARG _MEDIA_DIR=/app/staticfiles
ARG PYTHONPATH

# Set work directory
WORKDIR /app

# Copy uv binary (needed for proper venv operation)
COPY --from=builder /bin/uv /bin/uvx /bin/
COPY --from=builder /app/.venv /app/.venv

RUN groupadd ${_GROUP} && useradd --no-log-init -r --no-create-home -G ${_GROUP} ${_USER}

# Copy project
COPY --chmod=+x ./dockers/*.sh ./
COPY --chown=${_GROUP}:${_USER} ./src ./src

# Set environment variables
# VIRTUAL_ENV tells Python where the venv is, allowing it to find site-packages automatically
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/app/.venv/bin/:$PATH \
    VIRTUAL_ENV=/app/.venv \
    PYTHONPATH="/app/src:${PYTHONPATH:-}"

USER ${_USER}

ENTRYPOINT ["bash", "-c", "/app/entrypoint.sh"]

