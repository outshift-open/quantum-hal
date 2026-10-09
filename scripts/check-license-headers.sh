#!/usr/bin/env bash
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0
#
# Fails if any tracked or generated .proto/.go/.py/.yml/.yaml/.sh file is
# missing the repo's standard copyright/SPDX header within its first few
# lines. Companion to scripts/add-license-headers.sh, which stamps the
# header onto generated SDK output -- this script is the check that
# nothing (generated or hand-written) slips through without it.
#
# Usage: check-license-headers.sh

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

COPYRIGHT='Copyright 2026 Cisco Systems, Inc. and its affiliates'
SPDX='SPDX-License-Identifier: Apache-2.0'

# Files that are intentionally exempt -- third-party/vendor-supplied
# boilerplate we didn't author from scratch, not something this repo's
# header convention applies to.
EXCLUDE_FILES=(
  ".github/workflows/codeql.yml"
)

is_excluded() {
  local f="$1"
  for e in "${EXCLUDE_FILES[@]}"; do
    [ "$f" = "$e" ] && return 0
  done
  return 1
}

missing=()
checked=0
while IFS= read -r -d '' f; do
  is_excluded "$f" && continue
  [ -f "$f" ] || continue
  checked=$((checked + 1))

  head_text="$(head -n 10 "$f")"
  if ! grep -qF "$COPYRIGHT" <<<"$head_text" || ! grep -qF "$SPDX" <<<"$head_text"; then
    missing+=("$f")
  fi
done < <(
  git ls-files -z --cached --others --exclude-standard -- \
    '*.go' '*.py' '*.proto' '*.yml' '*.yaml' '*.sh'
)

if [ "${#missing[@]}" -gt 0 ]; then
  echo "Missing or incomplete license header in:" >&2
  printf '  %s\n' "${missing[@]}" >&2
  echo >&2
  echo "Expected within the first 10 lines:" >&2
  echo "  $COPYRIGHT" >&2
  echo "  $SPDX" >&2
  exit 1
fi

echo "License header check passed ($checked files checked)."
