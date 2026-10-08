#!/usr/bin/env bash
# Keep aafaqcs.netlify.app in step with the YouTube channel (run hourly by a systemd user timer).
# New uploads -> data/*.json + thumbnails -> build check -> push to GitHub -> Netlify publishes.
# Quiet: lowest CPU and disk priority. Log: ~/.local/state/aafaqcs/autoupdate.log
set -uo pipefail
cd "$(dirname "$0")"
LOG="$HOME/.local/state/aafaqcs/autoupdate.log"; mkdir -p "$(dirname "$LOG")"
exec >>"$LOG" 2>&1
echo "== $(date '+%F %T')"
out=$(nice -n 19 ionice -c3 python3 sync_youtube.py 2>&1); echo "$out"
if grep -q "new video(s)" <<<"$out"; then
  nice -n 19 python3 build.py && nice -n 19 python3 push_github.py "Auto: new YouTube video(s)" && nice -n 19 python3 push_pages.py "Auto: new YouTube video(s)"
fi
