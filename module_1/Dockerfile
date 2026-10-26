FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    curl \
    git \
    bash \
    ca-certificates \
    nano \
    procps \
    nodejs \
    npm \
    sudo \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Install OpenCode
RUN npm install -g opencode-ai

# Install ngrok
RUN curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
    | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
    | tee /etc/apt/sources.list.d/ngrok.list \
    && apt-get update && apt-get install -y ngrok \
    && rm -rf /var/lib/apt/lists/*

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

# Claude Code configuration: default settings + status line
COPY --chown=dev:dev settings.json /home/dev/.claude/settings.json
COPY --chown=dev:dev statusline.sh /home/dev/.claude/statusline.sh
RUN chmod +x /home/dev/.claude/statusline.sh

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Student shell quality-of-life improvements
RUN echo 'export PS1="ai-course:\\w\$ "' >> /home/dev/.bashrc && \
    echo 'alias ll="ls -alF"' >> /home/dev/.bashrc && \
    echo 'alias la="ls -A"' >> /home/dev/.bashrc && \
    echo 'alias l="ls -CF"' >> /home/dev/.bashrc && \
    echo 'alias python="python3"' >> /home/dev/.bashrc && \
    echo 'alias pip="pip3"' >> /home/dev/.bashrc

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["/bin/bash"]
