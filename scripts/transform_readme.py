#!/usr/bin/env python3
"""
Convert an examples README.md into an MDX guide with small post-processing.

Behavior:
- Read INPUT_FILE and determine TITLE from the first H1 (or use example name)
- Insert the Tabs import immediately after the H1 (or create an H1 from TITLE)
- Convert blockquote-style admonitions like:
  > **Note:**\n+  > line1\n+  > line2
  into:
  :::note\n  line1\n  line2\n  :::
- Rewrite absolute docs URLs back to site-relative paths
- Append a Source block when EXAMPLE_NAME is provided

Usage: transform_readme.py INPUT_FILE OUTPUT_FILE [EXAMPLE_NAME]
"""
from __future__ import annotations
import argparse
import os
import re
from pathlib import Path


# ANSI color codes
ANSI_RESET = '\x1b[0m'
ANSI_BOLD = '\x1b[1m'
ANSI_DARK_GRAY = '\x1b[90m'
ANSI_GREEN = '\x1b[92m'

# Import statement for Tabs component
TABS_IMPORT = 'import { Tabs, TabsContent, TabsList, TabsTrigger } from "zudoku/ui/Tabs"\n\n'

# Regex patterns
FENCE_PATTERN = re.compile(r"(^```([^\n]*)\n)(.*?)(\n```)$", flags=re.M | re.S)
FRONT_MATTER_PATTERN = re.compile(r"^---\n.*?\n---\n\s*", flags=re.S)
ADMONITION_PATTERN = re.compile(r"^>\s*\*\*([^*]+)\*\*:\s*$")


def extract_title(text: str, example_name: str | None) -> str:
    m = re.search(r"^# (.+)$", text, flags=re.M)
    if m:
        return m.group(1).strip()
    if example_name:
        return example_name
    return ""


def ensure_front_matter(text: str, title: str) -> str:
    """Ensure YAML front-matter with title at the top, replacing existing if present."""
    fm = f"---\ntitle: \"{title}\"\n---\n\n"
    m = FRONT_MATTER_PATTERN.match(text)
    if m:
        return fm + text[m.end():]
    return fm + text


def insert_tabs_import(text: str, title: str) -> str:
    """Insert Tabs import after front-matter or H1, avoiding duplicates."""
    # If import already exists, do nothing
    if "zudoku/ui/Tabs" in text:
        return text
    # If there's YAML front-matter at the top, insert after it.
    m_fm = FRONT_MATTER_PATTERN.match(text)
    if m_fm:
        insert_at = m_fm.end()
        return text[:insert_at] + TABS_IMPORT + text[insert_at:]

    # Find first H1 and insert after it
    m = re.search(r"(^# .+)$", text, flags=re.M)
    if m:
        insert_at = m.end(1)
        return text[:insert_at] + "\n" + TABS_IMPORT + text[insert_at:]

    # No front-matter nor H1: create H1 from title if available
    if title:
        return f"# {title}\n\n{TABS_IMPORT}\n" + text

    # Fallback: prepend import
    return TABS_IMPORT + "\n" + text


def convert_admonitions(text: str) -> str:
    """Convert blockquote-style admonitions to ::: syntax."""
    lines = text.splitlines()
    out = []
    i = 0

    while i < len(lines):
        m = ADMONITION_PATTERN.match(lines[i])
        if m:
            label = m.group(1).strip()
            key = label.lower().replace(" ", "-")
            i += 1
            block = []
            while i < len(lines) and re.match(r"^> ?", lines[i]):
                line = re.sub(r"^> ?", "", lines[i])
                block.append(line)
                i += 1
            # Start admonition block
            out.append(f":::{key}")
            out.extend(block)
            out.append(":::")
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def rewrite_urls(text: str) -> str:
    """Rewrite absolute docs URLs to site-relative paths."""
    # General rule for any other /docs/ link
    text = re.sub(r"https://unikraft.com/docs/([^\s\)]+)", r"/\1", text)
    return text


def color_bracket_and_bullet(line: str) -> str:
    """Color the [●] Deployed successfully! line."""
    line = line.replace('[', f'{ANSI_DARK_GRAY}[{ANSI_RESET}')
    line = line.replace('●', f'{ANSI_GREEN}●{ANSI_RESET}')
    line = line.replace(']', f'{ANSI_DARK_GRAY}]{ANSI_RESET}')
    return line


def color_box_drawing_line(line: str) -> str:
    """Color lines with box-drawing characters and labels."""
    # Match pattern like " ├────── name: value" or " │" (empty line)
    colon_match = re.search(r'^(\s*)((?:│|├|└))((?:─*)\s*)([^:]+)(:)(.*)$', line)

    if colon_match:
        leading_space = colon_match.group(1)  # leading whitespace
        box_char = colon_match.group(2)       # │, ├, or └
        dashes = colon_match.group(3)         # ─── and spaces
        label = colon_match.group(4)          # the label (e.g., "name")
        colon = colon_match.group(5)          # the colon
        value = colon_match.group(6)          # the value after colon

        # Color the box character
        box_colored = f'{ANSI_DARK_GRAY}{box_char}{ANSI_RESET}'

        # Color all dashes
        dashes_colored = dashes.replace('─', f'{ANSI_DARK_GRAY}─{ANSI_RESET}')

        # Color the label in dark gray (but not the colon)
        label_colored = f'{ANSI_DARK_GRAY}{label}{ANSI_RESET}{colon}'

        # Check if this is the state line and color the value in green
        if 'state' in label.lower():
            # Color the state value (first word after colon and spaces)
            value_match = re.search(r'^(\s*)(\S+)(.*)$', value)
            if value_match:
                value_spaces = value_match.group(1)
                state_value = value_match.group(2)
                rest = value_match.group(3)
                value = f'{value_spaces}{ANSI_GREEN}{state_value}{ANSI_RESET}{rest}'

        return leading_space + box_colored + dashes_colored + label_colored + value
    else:
        # No colon, just color the box-drawing characters
        for char in ['│', '├', '└', '─']:
            line = line.replace(char, f'{ANSI_DARK_GRAY}{char}{ANSI_RESET}')
        return line


def color_deployed_block(text: str) -> str:
    """Find and colorize deployed successfully blocks with ANSI codes."""
    def repl(m):
        fence_start = m.group(1)
        lang = (m.group(2) or "").strip()
        body = m.group(3)
        fence_end = m.group(4)

        # Only operate on blocks that contain the deployed-success marker text.
        if 'deployed successfully!' not in body.lower():
            return m.group(0)

        # Check if this block already has proper ANSI coloring applied
        if f'{ANSI_DARK_GRAY}│{ANSI_RESET}' in body or f'{ANSI_DARK_GRAY}├{ANSI_RESET}' in body:
            return m.group(0)

        # Ensure the fence is marked as 'ansi' for proper rendering
        if 'ansi' not in lang.lower():
            fence_start = "```ansi\n"

        # Process line by line to add colors
        lines = body.split('\n')
        colored_lines = []

        for line in lines:
            # Skip empty lines
            if not line.strip():
                colored_lines.append(line)
                continue

            # Color the bracket and bullet line: [●] Deployed successfully!
            if '●' in line and 'deployed successfully' in line.lower():
                colored_lines.append(color_bracket_and_bullet(line))
                continue

            # Color lines with box-drawing characters (│, ├, └, ─)
            if any(char in line for char in ['│', '├', '└', '─']):
                colored_lines.append(color_box_drawing_line(line))
            else:
                colored_lines.append(line)

        body = '\n'.join(colored_lines)
        return fence_start + body + fence_end

    return FENCE_PATTERN.sub(repl, text)


def find_state_column_index(header_line: str) -> int | None:
    """Find the index of the STATE column in a table header."""
    header_tokens = re.split(r"\s{2,}", header_line.strip())
    for i, token in enumerate(header_tokens):
        if token.strip().upper() == "STATE":
            return i
    return None


def bold_table_header(header_line: str) -> str:
    """Make each token in the table header bold."""
    pieces = re.split(r'(\s{2,})', header_line)
    cols = pieces[0::2]
    seps = pieces[1::2]

    for i, col in enumerate(cols):
        token = col.strip()
        if token and ANSI_BOLD not in token:
            cols[i] = col.replace(token, f"{ANSI_BOLD}{token}{ANSI_RESET}", 1)

    result = ""
    for i, col in enumerate(cols):
        result += col
        if i < len(seps):
            result += seps[i]
    return result


def color_state_value_in_row(line: str, state_col: int) -> str:
    """Color the state value in a table row."""
    pieces = re.split(r'(\s{2,})', line)
    cols = pieces[0::2]
    seps = pieces[1::2]

    if len(cols) > state_col:
        raw_val = cols[state_col]
        val = raw_val.strip()
        if val and ANSI_GREEN not in val:
            colored = f"{ANSI_GREEN}{val}{ANSI_RESET}"
            cols[state_col] = raw_val.replace(val, colored, 1)

    # Reconstruct using original separators to preserve spacing
    result = ""
    for i, col in enumerate(cols):
        result += col
        if i < len(seps):
            result += seps[i]
    return result


def color_state_in_table_blocks(text: str) -> str:
    """Color state values in table-style fenced blocks (STATE column) with light green."""
    def repl(m):
        fence_start = m.group(1)
        body = m.group(3)
        fence_end = m.group(4)

        lines = body.splitlines()

        # Find header line that contains NAME and STATE (case-insensitive)
        header_idx = None
        for idx, line in enumerate(lines):
            if re.search(r"\bNAME\b", line, flags=re.I) and re.search(r"\bSTATE\b", line, flags=re.I):
                header_idx = idx
                break

        if header_idx is None:
            return m.group(0)

        # Find the STATE column index
        state_col = find_state_column_index(lines[header_idx])
        if state_col is None:
            return m.group(0)

        # Process header: make each header token bold
        new_lines = lines[:header_idx]
        new_lines.append(bold_table_header(lines[header_idx]).rstrip('\n'))

        # Process data rows
        j = header_idx + 1
        while j < len(lines) and lines[j].strip() != "":
            new_lines.append(color_state_value_in_row(lines[j], state_col).rstrip('\n'))
            j += 1

        # Append any remaining lines
        new_lines.extend(lines[j:])
        new_body = "\n".join(new_lines)
        return fence_start + new_body + fence_end

    return FENCE_PATTERN.sub(repl, text)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the README to MDX transformation script."""
    p = argparse.ArgumentParser(
        description="Convert examples README.md into an MDX guide with ANSI coloring"
    )
    p.add_argument("input_file", help="Path to input README.md file")
    p.add_argument("output_file", help="Path to output MDX file")
    p.add_argument("example_name", nargs="?", default="", help="Optional example name for title")
    args = p.parse_args(argv)

    inp = Path(args.input_file)
    out = Path(args.output_file)
    example_name = args.example_name or None

    txt = inp.read_text(encoding="utf-8")

    # Determine title
    title = os.environ.get('TITLE') or extract_title(txt, example_name)

    # Apply transformations in sequence
    content = ensure_front_matter(txt, title)
    content = re.sub(r"(?m)^# .+\n", "", content, count=1)  # Remove first H1
    content = insert_tabs_import(content, title)
    content = convert_admonitions(content)
    content = rewrite_urls(content)
    content = color_deployed_block(content)
    content = color_state_in_table_blocks(content)

    out.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
