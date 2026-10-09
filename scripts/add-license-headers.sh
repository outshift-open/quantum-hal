#!/usr/bin/env bash
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0
#
# Prepends the repo's standard copyright/SPDX header to every generated
# Go/Python file under the given directories, using each file's own comment
# style. Idempotent: a file that already starts with the header is left
# untouched, so this is safe to run after every codegen invocation.
#
# Usage: add-license-headers.sh <dir> [<dir> ...]

set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: $0 <dir> [<dir> ...]" >&2
  exit 1
fi

SLASH_HEADER='// Copyright 2026 Cisco Systems, Inc. and its affiliates
//
// SPDX-License-Identifier: Apache-2.0
'

HASH_HEADER='# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0
'

stamp() {
  local file="$1" header="$2" marker="$3"
  if head -n1 "$file" | grep -qF "$marker"; then
    return
  fi
  local tmp
  tmp="$(mktemp)"
  printf '%s\n' "$header" >"$tmp"
  cat "$file" >>"$tmp"
  mv "$tmp" "$file"
}

for dir in "$@"; do
  [ -d "$dir" ] || continue

  while IFS= read -r -d '' file; do
    stamp "$file" "$SLASH_HEADER" "// Copyright 2026 Cisco Systems, Inc."
  done < <(find "$dir" -name '*.go' -print0)

  while IFS= read -r -d '' file; do
    stamp "$file" "$HASH_HEADER" "# Copyright 2026 Cisco Systems, Inc."
  done < <(find "$dir" \( -name '*.py' -o -name '*.pyi' \) -print0)
done
