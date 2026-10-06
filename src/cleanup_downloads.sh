#!/usr/bin/env bash
# Reclaim ~205 MB of duplicated ICPSR downloads in ~/Downloads.
# NOTHING here is unique — every file was verified present under
# data/raw/ before this list was written. Review, then run.
#
#   bash src/cleanup_downloads.sh --dry-run    (default, shows only)
#   bash src/cleanup_downloads.sh --delete     (actually removes)
set -euo pipefail
MODE="${1:---dry-run}"
cd ~/Downloads

TARGETS=(
  "ICPSR_02896"  "ICPSR_02896 2"  "ICPSR_02896 3"  "ICPSR_02896 4"
  "ICPSR_02896 5"  "ICPSR_02896 6"  "ICPSR_02896 7"  "ICPSR_02896 Data 32"
  "ICPSR_02896-V3.zip"  "ICPSR_02896-V3 (1).zip"  "ICPSR_02896-V3 (2).zip"
  "ICPSR_02896-V3 (3).zip"  "ICPSR_02896-V3_data_32.zip"
  "ICPSR_38927"  "ICPSR_38927-V1.zip"
)
# NOTE: "ICPSR_02896 8" (the complete 106-dataset archive, 528 MB) and
# "ICPSR_02896-V3 (4).zip" are deliberately NOT in this list. Keep at least
# one of them — the project holds only the 20 datasets it needs.

total=0
for t in "${TARGETS[@]}"; do
  if [ -e "$t" ]; then
    sz=$(du -sk "$t" | cut -f1); total=$((total+sz))
    printf '%8d MB  %s\n' "$((sz/1024))" "$t"
    [ "$MODE" = "--delete" ] && rm -rf "$t"
  fi
done
printf '\n%s: %d MB across %d items\n' \
  "$([ "$MODE" = "--delete" ] && echo DELETED || echo WOULD RECLAIM)" \
  "$((total/1024))" "${#TARGETS[@]}"
[ "$MODE" != "--delete" ] && echo 'Re-run with --delete to remove.'
