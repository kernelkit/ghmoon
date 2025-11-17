#!/usr/bin/env python3
"""
Convert ANSI escape sequences to GitHub Flavored Markdown compatible markup.

GFM supports limited HTML tags within <pre> blocks:
- <b>, <strong> for bold
- <i>, <em> for italics
- <mark> for highlighting
- <del> for strikethrough
- <ins> for underline

Since GFM doesn't support color styling, we use semantic markup instead.
"""

import re
import sys


# ANSI color/style codes we care about
ANSI_PATTERNS = {
    # Reset
    '[0m': '',
    '[00m': '',

    # Text styles (preservable in GFM)
    '[1m': '<b>',          # Bold
    '[01m': '<b>',
    '[21m': '</b>',        # Bold off
    '[22m': '</b>',        # Normal intensity
    '[2m': '<i>',          # Dim (use italic as approximation)
    '[02m': '<i>',
    '[3m': '<i>',          # Italic
    '[03m': '<i>',
    '[23m': '</i>',        # Italic off
    '[4m': '<ins>',        # Underline
    '[04m': '<ins>',
    '[24m': '</ins>',      # Underline off
    '[9m': '<del>',        # Strikethrough
    '[09m': '<del>',
    '[29m': '</del>',      # Strikethrough off

    # Foreground colors (strip, but could add emojis for semantic meaning)
    '[30m': '',   # Black
    '[31m': '',   # Red
    '[32m': '',   # Green
    '[33m': '',   # Yellow
    '[34m': '',   # Blue
    '[35m': '',   # Magenta
    '[36m': '',   # Cyan
    '[37m': '',   # White
    '[90m': '',   # Bright Black (Gray)
    '[91m': '',   # Bright Red
    '[92m': '',   # Bright Green
    '[93m': '',   # Bright Yellow
    '[94m': '',   # Bright Blue
    '[95m': '',   # Bright Magenta
    '[96m': '',   # Bright Cyan
    '[97m': '',   # Bright White

    # Background colors (use mark for any background)
    '[40m': '<mark>',   # Black bg
    '[41m': '<mark>',   # Red bg
    '[42m': '<mark>',   # Green bg
    '[43m': '<mark>',   # Yellow bg
    '[44m': '<mark>',   # Blue bg
    '[45m': '<mark>',   # Magenta bg
    '[46m': '<mark>',   # Cyan bg
    '[47m': '<mark>',   # White bg
    '[100m': '<mark>',  # Bright Black bg
    '[101m': '<mark>',  # Bright Red bg
    '[102m': '<mark>',  # Bright Green bg
    '[103m': '<mark>',  # Bright Yellow bg
    '[104m': '<mark>',  # Bright Blue bg
    '[105m': '<mark>',  # Bright Magenta bg
    '[106m': '<mark>',  # Bright Cyan bg
    '[107m': '<mark>',  # Bright White bg

    # Combined codes (common patterns)
    '[37;44m': '<mark><b>',  # White on blue (highlight)
    '[1;31m': '<b>',         # Bold red -> just bold
    '[1;32m': '<b>',         # Bold green -> just bold
    '[1;33m': '<b>',         # Bold yellow -> just bold
}


def convert_ansi_to_gfm(text):
    """Convert ANSI escape sequences to GFM-compatible HTML tags with semantic meaning."""

    lines = text.split('\n')
    clean_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        original_line = line

        # Check for semantic patterns at start of line
        # [93m at line start = <h1> (9PM main heading)
        if line.startswith('\x1b[93m'):
            # Remove the code
            line = line[5:]
            # Check if it ends with reset
            if '\x1b[0m' in line:
                line = line.replace('\x1b[0m', '')
            line = '<h1>' + line + '</h1>'
            clean_lines.append(line)
            i += 1
            continue

        # [0m[93m at line start - could be heading or skip
        if line.startswith('\x1b[0m\x1b[93m'):
            # Remove the leading codes (\x1b[0m = 4 bytes, \x1b[93m = 5 bytes)
            content = line[9:]

            # Check if there's actual content on this line (not just whitespace/newline)
            # Remove any trailing reset codes for this check
            test_content = content.replace('\x1b[0m', '').strip()

            if test_content:
                # Has content - this is a skip line, use <del>
                # Clean up any reset codes
                line = content.replace('\x1b[0m', '')
                line = '<del>' + line + '</del>'
                clean_lines.append(line)
                i += 1
                continue
            else:
                # Empty or just whitespace - could be heading on next line
                # Look ahead to see if next line has content
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Check if next line has content and no ANSI codes at start
                    if next_line and not next_line.startswith('\x1b['):
                        # Next line is the heading content
                        line = '<h2>' + next_line + '</h2>'
                        clean_lines.append(line)
                        i += 2  # Skip both this line and next line
                        continue

                # No content on next line, skip this empty line
                line = ''
                clean_lines.append(line)
                i += 1
                continue

        # Process other ANSI codes
        # [92m = pass (green - highlighted)
        line = re.sub(r'\x1b\[0m\x1b\[92m', '<mark><b>', line)
        line = re.sub(r'\x1b\[92m', '<mark><b>', line)

        # [91m = fail (red - bold)
        line = re.sub(r'\x1b\[0m\x1b\[91m', '<b>', line)
        line = re.sub(r'\x1b\[91m', '<b>', line)

        # [93m = skip/warning (yellow)
        # If followed immediately by a character (like 's'), it's a skip marker in summary
        # Use negative lookahead to check if NOT followed by [0m (which would be empty)
        line = re.sub(r'\x1b\[93m(?=[a-zA-Z])', '<del>', line)
        # Plain [93m (not followed by letter) = just bold
        line = re.sub(r'\x1b\[93m', '<b>', line)

        # [94m = new test/heading (blue - h3)
        line = re.sub(r'\x1b\[94m', '<h3>', line)

        # [2m = dim, just strip it (regular text)
        line = re.sub(r'\x1b\[0?2m', '', line)

        # [37;44m = white on blue (mark + bold)
        line = re.sub(r'\x1b\[37;44m', '<mark><b>', line)

        # Replace each [0m with appropriate closing tags
        # First, detect what tags are open
        def get_open_tags(text):
            """Scan text to find unclosed HTML tags"""
            tags = []
            # Track opens and closes
            if '<mark><b>' in text:
                tags.extend(['mark', 'b'])
            elif '<b>' in text:
                tags.append('b')
            if '<del>' in text and '</del>' not in text:
                tags.append('del')
            if '<h3>' in text and '</h3>' not in text:
                tags.append('h3')

            # Remove tags that are already closed
            if '</b></mark>' in text or ('</b>' in text and '</mark>' in text):
                if 'b' in tags:
                    tags.remove('b')
                if 'mark' in tags:
                    tags.remove('mark')
            elif '</b>' in text and 'b' in tags:
                tags.remove('b')
            elif '</mark>' in text and 'mark' in tags:
                tags.remove('mark')
            elif '</del>' in text and 'del' in tags:
                tags.remove('del')

            return tags

        # Replace [0m codes with closing tags
        while '\x1b[0m' in line:
            open_tags = get_open_tags(line)
            if not open_tags:
                # No tags to close, just remove the code
                line = line.replace('\x1b[0m', '', 1)
                continue

            # Close tags in proper order
            closing = ''
            if 'b' in open_tags and 'mark' in open_tags:
                closing = '</b></mark>'
            elif 'del' in open_tags:
                closing = '</del>'
            elif 'b' in open_tags:
                closing = '</b>'
            elif 'h3' in open_tags:
                closing = '</h3>'
            elif 'mark' in open_tags:
                closing = '</mark>'
            else:
                closing = ''  # Nothing to close

            # Replace first occurrence of [0m
            line = line.replace('\x1b[0m', closing, 1)

        # Clean up any remaining reset codes
        line = line.replace('\x1b[00m', '')

        # Clean up any remaining ANSI codes we didn't handle
        line = re.sub(r'\x1b\[[0-9;]*m', '', line)

        # Auto-close any tags still open at end of line
        # This handles cases where reset code is on next line
        final_open_tags = get_open_tags(line)
        if final_open_tags:
            closing = ''
            if 'b' in final_open_tags and 'mark' in final_open_tags:
                closing = '</b></mark>'
            elif 'del' in final_open_tags:
                closing = '</del>'
            elif 'b' in final_open_tags:
                closing = '</b>'
            elif 'h3' in final_open_tags:
                closing = '</h3>'
            elif 'mark' in final_open_tags:
                closing = '</mark>'
            line += closing

        clean_lines.append(line)
        i += 1

    return '\n'.join(clean_lines)


def main():
    """Read from stdin or file, convert ANSI to GFM, write to stdout."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert ANSI escape sequences to GFM-compatible markup'
    )
    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='Input file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output file (default: stdout)'
    )

    args = parser.parse_args()

    content = args.input.read()
    converted = convert_ansi_to_gfm(content)
    args.output.write(converted)


if __name__ == '__main__':
    main()
