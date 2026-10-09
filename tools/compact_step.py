"""Remove indentation outside STEP strings/comments without changing tokens.

This makes large text STEP exports easier to publish. Preserve all quoted text,
line endings, entities, numbers and topology. Always run the geometry round-trip
audit after formatting; byte reduction alone is not geometric verification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def compact(path):
    original = path.read_bytes()
    if not original.startswith(b'ISO-10303-21;') or not original.rstrip().endswith(b'END-ISO-10303-21;'):
        raise ValueError(f'Not a complete STEP Part 21 file: {path}')
    quoted = comment = False
    lines = []
    for line in original.splitlines(keepends=True):
        lines.append(line if quoted or comment else line.lstrip(b' \t'))
        # Doubled apostrophes inside strings toggle twice, preserving end state.
        for match in re.finditer(rb"'|/\*|\*/", line):
            token = match.group()
            if token == b"'" and not comment:
                quoted = not quoted
            elif token == b'/*' and not quoted:
                comment = True
            elif token == b'*/' and not quoted:
                comment = False
    if quoted or comment:
        raise ValueError(f'Unterminated STEP string/comment: {path}')
    formatted = b''.join(lines)
    tmp = path.with_suffix(path.suffix + '.formatting-tmp')
    tmp.write_bytes(formatted)
    tmp.replace(path)
    return {'file': str(path), 'original_bytes': len(original), 'bytes': len(formatted),
            'removed_indentation_bytes': len(original)-len(formatted),
            'original_sha256': hashlib.sha256(original).hexdigest(),
            'sha256': hashlib.sha256(formatted).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    rows = [compact(path) for path in args.files]
    report = {'passed': True, 'scope': 'Whitespace formatting only; geometry acceptance is recorded in the separate STEP round-trip audit.', 'files': rows}
    args.report.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
