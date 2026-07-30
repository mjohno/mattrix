# Mattrix runtime image: Debian, Python, and the Pi execution harness.
FROM debian:bookworm-slim

ARG TARGETARCH
ARG NODE_VERSION=22.19.0
ARG PI_VERSION=0.81.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        python3 \
        python3-pip \
        python3-venv \
        xz-utils \
    && case "${TARGETARCH}" in \
        amd64) node_arch=x64 ;; \
        arm64) node_arch=arm64 ;; \
        *) echo "Unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${node_arch}.tar.xz" \
        -o /tmp/node.tar.xz \
    && tar -xJf /tmp/node.tar.xz --strip-components=1 -C /usr/local \
    && rm /tmp/node.tar.xz \
    && apt-get purge -y --auto-remove curl xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN npm install --global "@earendil-works/pi-coding-agent@${PI_VERSION}"

RUN groupadd --gid 1000 mattrix \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash mattrix

WORKDIR /opt/mattrix
COPY --chown=mattrix:mattrix . /opt/mattrix

RUN python3 -m venv /opt/stagger-step-venv \
    && /opt/stagger-step-venv/bin/pip install --no-cache-dir /opt/mattrix/agents/stagger-step

ENV PATH="/opt/stagger-step-venv/bin:${PATH}"
USER mattrix
ENTRYPOINT ["/bin/bash"]
