#!/usr/bin/env bash
set -e
TARGET="http://127.0.0.1:5000"
LABEL="${1:-scan}"
mkdir -p evidence/dast
docker run --rm --network host -v "$(pwd)/evidence/dast:/zap/wrk:rw" \
  ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t "$TARGET" -r "zap_${LABEL}.html" -I
echo "Report: evidence/dast/zap_${LABEL}.html"
