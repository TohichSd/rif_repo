#!/usr/bin/env bash
set -euo pipefail

: "${HEROKU_APP_NAME:?Set HEROKU_APP_NAME in CircleCI}"
: "${HEROKU_API_KEY:?Set HEROKU_API_KEY in CircleCI}"
: "${HEROKU_APP_URL:?Set HEROKU_APP_URL in CircleCI}"

auth_dir="$(mktemp -d)"
trap 'rm -rf "$auth_dir"' EXIT

cat > "$auth_dir/askpass" <<'ASKPASS'
#!/bin/sh
case "$1" in
    *Username*) printf '%s\n' heroku ;;
    *Password*) printf '%s\n' "$HEROKU_API_KEY" ;;
    *) exit 1 ;;
esac
ASKPASS
chmod 700 "$auth_dir/askpass"

LC_ALL=C GIT_ASKPASS="$auth_dir/askpass" GIT_TERMINAL_PROMPT=0 \
    git -c credential.helper= push "https://git.heroku.com/$HEROKU_APP_NAME.git" \
    HEAD:refs/heads/main
