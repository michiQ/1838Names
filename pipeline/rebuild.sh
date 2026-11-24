#!/bin/bash
# Full rebuild from the COMMITTED database (never a stale /tmp copy).
# Usage (from repo root): bash pipeline/rebuild.sh
# Then: python3 pipeline/stability_hash.py > /tmp/h1.txt ; run again ; diff (must be identical).
set -e
cd "$(dirname "$0")/.."
git show HEAD:black_metropolis.db > /tmp/black_metropolis.db
export BM_DB=/tmp/black_metropolis.db
cd pipeline
for s in import_1811_directory import_1838_register match_names load_extractions load_coppin load_storymaps split_nichols split_swilliams split_bassett split_appearances apply_merges load_nolibs load_ugrr load_blogs load_mobstats apply_merges find_merge_candidates build_viewer; do
  echo "== $s"; python3 $s.py 2>&1 | tail -3
done
