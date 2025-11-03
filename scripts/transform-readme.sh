#!/usr/bin/env bash
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025, Unikraft GmbH.
# Licensed under the BSD-3-Clause License (the "License").
# You may not use this file except in compliance with the License.

set -euo pipefail

INPUT_FILE="${1:?Input file required}"
OUTPUT_FILE="${2:?Output file required}"
EXAMPLE_NAME="${3:-}"

# Extract title from first H1 line, or use example name
TITLE="$(grep -m1 -E '^# ' "$INPUT_FILE" | sed 's/^# //' || echo "$EXAMPLE_NAME")"

# Convert README.md to .mdx format
# This can be extended to:
# - Add front-matter
# - Convert markdown fenced code blocks if needed
# - Rewrite relative links
# - Add custom components

# For now, just copy the content
# You can add transformations here as needed
cp "$INPUT_FILE" "$OUTPUT_FILE"
