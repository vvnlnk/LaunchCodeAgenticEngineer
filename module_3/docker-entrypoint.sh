#!/bin/bash
set -eu

AUTH_DIR=/claude-auth
APP_USER=dev

# Stage 1 (root): match the "dev" user to the owner of the bind-mounted
# /workspace (or HOST_UID/HOST_GID), so files created in the container are
# owned by the host user. Then re-run this script as that user.
if [ "$(id -u)" = 0 ]; then
  uid=${HOST_UID:-$(stat -c %u /workspace)}
  gid=${HOST_GID:-$(stat -c %g /workspace)}
  # A root-owned workspace (or none mounted) falls back to the image default.
  [ "$uid" = 0 ] && uid=1000
  [ "$gid" = 0 ] && gid=1000

  [ "$(id -g "$APP_USER")" = "$gid" ] || groupmod -o -g "$gid" "$APP_USER"
  [ "$(id -u "$APP_USER")" = "$uid" ] || usermod -o -u "$uid" "$APP_USER"
  chown -R "$uid:$gid" "/home/$APP_USER"

  # The auth volume is shared across course images, and older ones ran as
  # root, so reclaim the persisted credential on every start.
  mkdir -p "$AUTH_DIR"
  chown -R "$uid:$gid" "$AUTH_DIR"

  exec setpriv --reuid="$uid" --regid="$gid" --init-groups \
    env HOME="/home/$APP_USER" USER="$APP_USER" LOGNAME="$APP_USER" "$0" "$@"
fi

# Stage 2 (dev): group-writable files so other agents/users sharing the
# group can edit them too.
umask 0002
mkdir -p "$HOME/.claude"

# A persisted credential means this is NOT the first run: restore it and mark
# onboarding complete so Claude skips the first-run flow (theme, login, trust).
# On the first run there is no credential, so onboarding runs once and the
# background saver below persists the resulting credential.
if [ -f "$AUTH_DIR/.credentials.json" ]; then
  cp "$AUTH_DIR/.credentials.json" "$HOME/.claude/.credentials.json"
  chmod 600 "$HOME/.claude/.credentials.json"
  echo '{ "hasCompletedOnboarding": true, "projects": { "/workspace": { "hasTrustDialogAccepted": true } } }' > "$HOME/.claude.json"
fi

# Register this image's MCP servers (merged into $HOME/.claude.json).
claude mcp add slack \
  node /usr/local/lib/node_modules/@modelcontextprotocol/server-slack/dist/index.js \
  -e SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
  -e SLACK_TEAM_ID="$SLACK_TEAM_ID"

claude mcp add gmail \
  node /usr/local/lib/node_modules/@gongrzhe/server-gmail-autoauth-mcp/build/index.js

# Save the credential whenever it changes, so login survives any exit. Save
# when the persisted copy is missing (first login) or older than the live one;
# temp-file + chmod + atomic mv keeps the copy safe on the shared volume.
( set +e
  while true; do
    if [ -f "$HOME/.claude/.credentials.json" ] && \
       { [ ! -f "$AUTH_DIR/.credentials.json" ] || \
         [ "$HOME/.claude/.credentials.json" -nt "$AUTH_DIR/.credentials.json" ]; }; then
      tmp=$(mktemp "$AUTH_DIR/.credentials.json.tmp.XXXXXX")
      cp "$HOME/.claude/.credentials.json" "$tmp"
      chmod 600 "$tmp"
      mv -f "$tmp" "$AUTH_DIR/.credentials.json"
    fi
    sleep 5
  done ) &

# exec so the command runs as PID 1 (correct signal handling / reaping).
exec "$@"
