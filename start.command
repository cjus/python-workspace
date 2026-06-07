#!/usr/bin/env bash
# Double-clickable macOS launcher: just runs ./start.sh from this folder.
# (If macOS blocks it the first time, right-click -> Open.)
cd "$(dirname "$0")"
exec ./start.sh
