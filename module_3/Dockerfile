FROM python:3.12-slim

WORKDIR /workspace

# --- Environment variables ---
# Prevent .pyc files and enable unbuffered output for cleaner container logs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    # HuggingFace / Sentence Transformers cache inside the workspace so it
    # persists across container runs when /workspace is bind-mounted.
    # These dirs are created below; if /workspace is bind-mounted the host
    # directory will shadow them, but HF will re-create subdirs as needed.
    HF_HOME=/workspace/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/workspace/.cache/sentence-transformers \
    HOST=0.0.0.0 \
    CLIENT_PORT=8502

# --- OS packages ---
# Core tools (curl, git, etc.) plus Module 3.2 diagnostics/build dependencies:
#   build-essential / python3-dev  — compile Python packages with C extensions
#   sqlite3                        — inspect SQLite DBs used by storage MCP server
#   jq                             — parse/pretty-print JSON from MCP responses
#   unzip / less / tree            — general file inspection
#   iproute2 / net-tools / lsof    — inspect listening ports and network state
#   dnsutils                       — DNS lookup inside the container
#   make                           — run Makefiles in lesson starter kits
RUN apt-get update && apt-get install -y \
    curl \
    git \
    bash \
    ca-certificates \
    nano \
    procps \
    nodejs \
    npm \
    gettext-base \
    sudo \
    build-essential \
    python3-dev \
    sqlite3 \
    jq \
    unzip \
    less \
    tree \
    iproute2 \
    net-tools \
    lsof \
    dnsutils \
    make \
    && rm -rf /var/lib/apt/lists/*

# --- Python packages ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify critical Module 3.2 imports so the build fails fast on a bad package
# rather than surprising students at runtime.
RUN python3 -c "\
import fastmcp; \
import mcp; \
import aiosqlite; \
import chromadb; \
import sentence_transformers; \
import sklearn; \
import pydantic; \
import httpx; \
import rank_bm25; \
import sqlite_vec; \
print('All Module 3.2 imports OK')"

# --- Node/npm agent tooling ---
# Claude Code is the primary agent harness for this course.
RUN npm install -g @anthropic-ai/claude-code

# OpenCode is supported as an alternative harness.
RUN npm install -g opencode-ai

# MCP servers for Slack and Gmail integrations.
RUN npm install -g @modelcontextprotocol/server-slack
RUN npm install -g @gongrzhe/server-gmail-autoauth-mcp

# Verify Node tooling versions (non-fatal for version flags, fatal for missing binaries).
RUN node --version && \
    npm --version && \
    (claude --version 2>/dev/null || claude version 2>/dev/null || echo "claude installed (no --version flag)") && \
    (opencode --version 2>/dev/null || opencode version 2>/dev/null || echo "opencode installed (no --version flag)")

# --- ngrok ---
RUN curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
    | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
    | tee /etc/apt/sources.list.d/ngrok.list \
    && apt-get update && apt-get install -y ngrok \
    && rm -rf /var/lib/apt/lists/*

# --- Non-root user ---
# Non-root user. The entrypoint remaps its UID/GID at runtime to match the
# owner of the bind-mounted /workspace, so files stay editable on the host.
# Passwordless sudo keeps apt/global installs possible.
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID dev \
    && useradd -m -u $UID -g $GID -s /bin/bash dev \
    && echo 'dev ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/dev \
    && chmod 440 /etc/sudoers.d/dev \
    && chown dev:dev /workspace

# Global npm dir is root-owned, so Claude Code can't self-update; user pip
# installs land in ~/.local.
ENV DISABLE_AUTOUPDATER=1 \
    PATH=/home/dev/.local/bin:$PATH

# --- Claude Code configuration ---
COPY --chown=dev:dev skills/ /home/dev/.claude/skills/

COPY --chown=dev:dev agents/ /home/dev/.claude/agents/

# Default settings + status line
COPY --chown=dev:dev settings.json /home/dev/.claude/settings.json
COPY --chown=dev:dev statusline.sh /home/dev/.claude/statusline.sh
RUN chmod +x /home/dev/.claude/statusline.sh

# --- Workspace directory structure for Module 3.2 ---
# /workspace itself is typically bind-mounted, so these dirs may be shadowed
# at runtime. Creating them here ensures they exist in the image-only case
# and documents the expected layout for the lesson.
RUN mkdir -p \
    /workspace/mcp-servers/storage \
    /workspace/mcp-servers/retrieval \
    /workspace/.cache/huggingface \
    /workspace/.cache/sentence-transformers \
    /workspace/docs \
    /workspace/tests \
    /memory/reference \
    && chown -R dev:dev /workspace /memory

# Bake the reference corpus into the image so the retrieval server works
# without a bind-mount. Mounting -v "$PWD/.memory":/memory at runtime
# will shadow this with a live corpus for development use.
COPY --chown=dev:dev .memory/reference/ /memory/reference/

# --- Entrypoint ---
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# --- Shell quality-of-life for learners ---
RUN echo 'export PS1="ai-course:\w\$ "' >> /home/dev/.bashrc && \
    echo 'alias ll="ls -alF"' >> /home/dev/.bashrc && \
    echo 'alias la="ls -A"' >> /home/dev/.bashrc && \
    echo 'alias l="ls -CF"' >> /home/dev/.bashrc && \
    echo 'alias python="python3"' >> /home/dev/.bashrc && \
    echo 'alias py="python3"' >> /home/dev/.bashrc && \
    echo 'alias pip="pip3"' >> /home/dev/.bashrc && \
    echo 'alias ports="lsof -i -P -n"' >> /home/dev/.bashrc && \
    echo 'alias mcp-servers="find /workspace/mcp-servers -maxdepth 3 -type f | sort"' >> /home/dev/.bashrc

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["/bin/bash"]
