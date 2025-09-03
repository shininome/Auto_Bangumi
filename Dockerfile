# Multi-stage Dockerfile for Auto_Bangumi
# Stage 1: Python base runtime
FROM alpine:3.18 AS python-base

ENV LANG="C.UTF-8" \
    TZ=Asia/Shanghai \
    PUID=1000 \
    PGID=1000 \
    UMASK=022 \
    VENV_PATH="/opt/venv"

# Install runtime system packages
RUN set -ex && \
    apk add --no-cache \
    bash \
    busybox-suid \
    python3 \
    py3-aiohttp \
    py3-bcrypt \
    curl \
    su-exec \
    shadow \
    tini \
    openssl \
    tzdata && \
    # Set timezone
    ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# Stage 2: Build dependencies
FROM python-base AS build-deps

# Install build tools and dependencies
RUN set -ex && \
    apk add --no-cache \
    build-base \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev \
    rust \
    cargo

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.cargo/bin/uv /usr/local/bin/uv && \
    uv --version

# Stage 3: Python virtual environment
FROM build-deps AS python-venv

ENV PATH="${VENV_PATH}/bin:${PATH}"

WORKDIR /app

# Copy Python project files
COPY backend/pyproject.toml backend/uv.lock ./

# Create virtual environment and install dependencies
RUN set -ex && \
    # Check if lock file exists and is readable
    ls -la uv.lock && \
    # Create virtual environment
    python3 -m venv ${VENV_PATH} && \
    # Install dependencies using uv
    uv sync --frozen --no-dev && \
    # Clear cache
    rm -rf /root/.cache

# Stage 4: Final runtime image
FROM python-base AS final

ENV PATH="/root/.local/bin:${VENV_PATH}/bin:${PATH}"

WORKDIR /app

# Copy virtual environment from build stage
COPY --from=python-venv --chown=root:root ${VENV_PATH} ${VENV_PATH}

# Add user
RUN set -ex && \
    mkdir -p /home/ab && \
    addgroup -S ab -g 911 && \
    adduser -S ab -G ab -h /home/ab -s /sbin/nologin -u 911

# Copy application code and scripts
COPY --chmod=755 backend/src/. .
COPY --chmod=755 entrypoint.sh /entrypoint.sh

# Set proper permissions
RUN chown -R ab:ab /app /home/ab

ENTRYPOINT ["tini", "-g", "--", "/entrypoint.sh"]

EXPOSE 7892
VOLUME [ "/app/config" , "/app/data" ]