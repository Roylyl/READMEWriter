#!/usr/bin/env python3
"""Offline README lint and claim/evidence integrity checks. Python 3.9+.

SPDX-License-Identifier: GPL-3.0-only
Copyright (c) 2026 Roylyl
"""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit


def mask_code(text):
    """Preserve offsets while masking fenced/indented code and comments."""
    out, fence = [], None
    for line in text.splitlines(keepends=True):
        match = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            if re.match(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(len(fence)) + r',}\s*$', line):
                fence = None
            out.append(''.join('\n' if c == '\n' else ' ' for c in line))
        elif match:
            fence = match[1]
            out.append(''.join('\n' if c == '\n' else ' ' for c in line))
        elif line.startswith(('    ', '\t')):
            out.append(''.join('\n' if c == '\n' else ' ' for c in line))
        else:
            out.append(line)
    text = ''.join(out)
    return re.sub(r'<!--.*?-->', lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), text, flags=re.S)


def mask_inline(text):
    return re.sub(r'(`+)([^`]|(?!\1)`)*?\1', lambda m: ' ' * len(m[0]), text)


def label_key(label):
    return ' '.join(label.split()).casefold()


def markdown_links(text):
    """Common inline and reference links, including balanced URL parentheses.

    Returns (url, image, offset); intentionally not a complete CommonMark parser.
    """
    text = mask_inline(text)
    definitions = {}
    pattern = r'^ {0,3}\[([^\]\n]+)\]:\s*(<[^>\n]+>|\S+)'
    for m in re.finditer(pattern, text, re.M):
        definitions[label_key(m[1])] = m[2].strip('<>')
    text = re.sub(pattern, lambda m: ' ' * len(m[0]), text, flags=re.M)
    i = 0
    while i < len(text):
        if text[i] != '[' or (i and text[i-1] == '\\'):
            i += 1
            continue
        image = i > 0 and text[i-1] == '!'
        start, depth, j = i, 1, i + 1
        while j < len(text) and depth:
            if text[j] == '\\':
                j += 2
                continue
            if text[j] == '[': depth += 1
            if text[j] == ']': depth -= 1
            j += 1
        if depth:
            i += 1
            continue
        label = text[i+1:j-1]
        if j < len(text) and text[j] == '(':
            k = j+1
            while k < len(text) and text[k].isspace(): k += 1
            if k < len(text) and text[k] == '<':
                end = text.find('>', k+1)
                if end != -1: yield text[k+1:end], image, start
            else:
                end, parens = k, 0
                while end < len(text):
                    c = text[end]
                    if c == '\\':
                        end += 2
                        continue
                    if c == '(':
                        parens += 1
                    elif c == ')':
                        if not parens: break
                        parens -= 1
                    elif c.isspace() and not parens: break
                    end += 1
                if end > k:
                    yield re.sub(r'\\([() ])', r'\1', text[k:end]), image, start
        elif j < len(text) and text[j] == '[':
            end = text.find(']', j+1)
            if end != -1:
                key = label_key(text[j+1:end] or label)
                yield definitions.get(key, 'readme-unresolved:' + key), image, start
        elif label_key(label) in definitions:
            yield definitions[label_key(label)], image, start
        # Advance inside label too, to see images nested within badge links.
        i += 1


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.headings = [], set(), []
        self.heading = None
        self.lines = [0]
        for m in re.finditer('\n', text): self.lines.append(m.end())
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        offset = self.lines[self.getpos()[0]-1] + self.getpos()[1]
        for attr in ('id', 'name' if tag == 'a' else 'id'):
            if attrs.get(attr): self.ids.add(attrs[attr])
        if tag in ('img', 'source'):
            if attrs.get('src'): self.links.append((attrs['src'], True, offset))
            if attrs.get('srcset'):
                for candidate in attrs['srcset'].split(','):
                    if candidate.strip(): self.links.append((candidate.split()[0], True, offset))
        if tag == 'a' and attrs.get('href'):
            self.links.append((attrs['href'], False, offset))
        if re.fullmatch(r'h[1-6]', tag): self.heading = [int(tag[1]), '', offset]

    def handle_endtag(self, tag):
        if self.heading and tag == 'h' + str(self.heading[0]):
            self.headings.append(tuple(self.heading))
            self.heading = None

    def handle_data(self, data):
        if self.heading: self.heading[1] += data


def slug(text):
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = html.unescape(re.sub(r'<[^>]+>', '', text)).lower()
    text = text.replace('`', '').replace('*', '').replace('~', '')
    return ''.join(c for c in text if c in '-_ ' or unicodedata.category(c)[0] in 'LMN').replace(' ', '-')


def document_info(text):
    clean = mask_code(text)
    elements = Elements(clean)
    headings = list(elements.headings)
    for m in re.finditer(r'^ {0,3}(#{1,6})[ \t]+(.+?)\s*#*\s*$', clean, re.M):
        headings.append((len(m[1]), m[2], m.start()))
    for m in re.finditer(r'^([^\n]+)\n {0,3}(=+|-+)[ \t]*$', clean, re.M):
        if not re.match(r'^\s*(?:#|[<>|])', m[1]):
            headings.append((1 if m[2][0] == '=' else 2, m[1], m.start()))
    anchors, used = set(elements.ids), set()
    for level, title, pos in sorted(headings, key=lambda x: x[2]):
        base = slug(title)
        anchor, suffix = base, 0
        while anchor in used:
            suffix += 1
            anchor = base + '-' + str(suffix)
        used.add(anchor)
        anchors.add(anchor)
    return clean, elements, headings, anchors


def case_path(path):
    """Find existing path while checking component case even on macOS."""
    path = Path(path).absolute()
    cursor, wrong = Path(path.anchor), False
    for part in path.parts[1:]:
        if part == '.': continue
        if part == '..':
            cursor = cursor.parent
            continue
        try:
            names = [entry.name for entry in cursor.iterdir()]
        except OSError:
            return None, wrong
        if part in names:
            cursor /= part
        else:
            matches = [n for n in names if n.casefold() == part.casefold()]
            if not matches: return None, wrong
            cursor /= matches[0]
            wrong = True
    return cursor if cursor.exists() else None, wrong


def repo_id(value):
    if not value: return None
    value = value.strip().removesuffix('.git').rstrip('/')
    m = re.search(r'(?:github\.com[/:])([^/\s]+/[^/\s]+)$', value)
    if m: return m[1]
    if re.fullmatch(r'[\w.-]+/[\w.-]+', value): return value
    return None


def detect_repo(root):
    try:
        result = subprocess.run(['git', '-C', str(root), 'config', '--get', 'remote.origin.url'],
                                capture_output=True, text=True, timeout=3)
        return repo_id(result.stdout)
    except (OSError, subprocess.TimeoutExpired):
        return None


def badge_repo(url):
    parts = urlsplit(url)
    if parts.hostname not in ('img.shields.io', 'shields.io'): return None
    tokens = unquote(parts.path).strip('/').split('/')
    if not tokens or tokens[0] != 'github': return None
    # Shields paths with additional metric segments before owner/repo.
    offset = 2
    if len(tokens) > 2 and tokens[1] in ('v', 'actions', 'issues', 'issues-pr', 'issues-closed', 'issues-pr-closed'):
        if tokens[1] in ('issues', 'issues-pr', 'issues-closed', 'issues-pr-closed'):
            offset = 3 if tokens[2] in ('detail',) else 2
        else:
            offset = 4 if tokens[1:4] == ['actions', 'workflow', 'status'] else 3
    return '/'.join(tokens[offset:offset+2]) if len(tokens) >= offset+2 else None


def lint(readme, root=None, expected_repo=None, allowed_repos=(), evidence=None):
    readme = Path(readme).absolute()
    root = Path(root or readme.parent).resolve()
    findings = []
    def add(code, message, offset=0, severity='error'):
        findings.append({'code': code, 'severity': severity, 'line': text[:offset].count('\n')+1,
                         'message': message})
    try:
        text = readme.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        return [{'code': 'read-error', 'severity': 'error', 'line': 1, 'message': str(exc)}]
    clean, elements, headings, anchors = document_info(text)
    h1s = [h for h in headings if h[0] == 1]
    if len(h1s) > 1: add('duplicate-h1', 'More than one H1 heading.', h1s[1][2])
    if not h1s: add('missing-h1', 'No H1 heading found.', severity='warning')
    for m in re.finditer(r'\{\{[^{}\n]+\}\}|\b(?:TODO|FIXME|TBD|YOUR_[A-Z_]+)\b|<(?:PROJECT_NAME|REPO_URL|OWNER)>', text):
        add('placeholder', 'Unresolved placeholder: ' + m[0], m.start())
    # Inspect code examples as well, but remove web URLs before path scanning.
    path_text = re.sub(r'https?://[^\s<>"\)]+', lambda m: ' ' * len(m[0]), text)
    pattern = r'file://[^\s<>]+|(?<![\w/])(?:/Users/|/home/|/private/|/tmp/|/Volumes/|/var/folders/)[^\s`<>"\)]+|(?<![\w])[A-Za-z]:(?!//)[\\/][^\s`<>"\)]+|\\\\[A-Za-z0-9_.-]+\\[^\s`<>"\)]+'
    for m in re.finditer(pattern, path_text):
        add('local-absolute-path', 'Machine-local absolute path: ' + m[0], m.start())
    expected_repo = expected_repo or detect_repo(root)
    allowed = {r.casefold() for r in allowed_repos}
    if expected_repo: allowed.add(expected_repo.casefold())
    links = list(markdown_links(clean)) + elements.links
    seen = set()
    for raw, image, pos in links:
        url = html.unescape(raw)
        key = (url, image, pos)
        if key in seen: continue
        seen.add(key)
        if url.startswith('readme-unresolved:'):
            add('undefined-reference', 'Undefined reference label: ' + url.split(':', 1)[1], pos)
            continue
        try: parsed = urlsplit(url)
        except ValueError:
            add('invalid-url', 'Malformed URL: ' + url, pos)
            continue
        badge = badge_repo(url)
        if badge:
            if not expected_repo:
                add('badge-repo-unverified', 'No GitHub origin or --repo; badge identity not checked: ' + badge, pos, 'warning')
            elif badge.casefold() not in allowed:
                add('badge-repo-mismatch', 'Badge references ' + badge + '; expected ' + expected_repo, pos)
        if parsed.scheme or parsed.netloc: continue
        path = unquote(parsed.path)
        fragment = unquote(parsed.fragment)
        if not path:
            target = readme
        elif path.startswith('/'):
            # GitHub /owner/repo links are site-root URLs, not local files.
            add('root-relative-link', 'Site-root link not checked; prefer a relative file link or full URL: ' + url, pos, 'warning')
            continue
        else:
            target = readme.parent / path
        resolved, wrong_case = case_path(target)
        if not resolved:
            add('missing-image' if image else 'missing-file', 'Referenced file does not exist: ' + url, pos)
            continue
        if wrong_case: add('path-case', 'Path capitalization differs from the filesystem: ' + path, pos)
        if not resolved.resolve().is_relative_to(root):
            add('outside-root', 'Link resolves outside --root: ' + url, pos)
            continue
        if fragment and not image:
            if resolved.suffix.lower() in ('.md', '.markdown'):
                try: other_anchors = anchors if resolved == readme else document_info(resolved.read_text(encoding='utf-8'))[3]
                except (OSError, UnicodeError):
                    add('read-error', 'Cannot read anchor target: ' + path, pos)
                    continue
                if fragment not in other_anchors: add('invalid-anchor', 'Anchor not found: ' + url, pos)
            elif resolved.suffix.lower() in ('.html', '.htm'):
                try: other_anchors = Elements(resolved.read_text(encoding='utf-8')).ids
                except (OSError, UnicodeError):
                    add('read-error', 'Cannot read HTML anchor target: ' + path, pos)
                    continue
                if fragment not in other_anchors: add('invalid-anchor', 'HTML anchor not found: ' + url, pos)
    if evidence:
        check_evidence(Path(evidence), root, text, add)
    return findings


def check_evidence(file, root, text, add):
    """Integrity only: a quote/hash match does not prove semantic entailment."""
    try:
        data = json.loads(file.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as exc:
        add('evidence-schema', 'Cannot load evidence JSON: ' + str(exc))
        return
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('claims'), list):
        add('evidence-schema', 'Expected schema_version=1 and a claims array.')
        return
    ids = set()
    levels = {'configuration', 'implementation', 'build', 'simulation', 'device', 'release', 'unknown'}
    for claim in data['claims']:
        if not isinstance(claim, dict) or not isinstance(claim.get('id'), str) or not isinstance(claim.get('quote'), str) or not claim.get('quote') or claim.get('level') not in levels or not isinstance(claim.get('evidence'), list):
            add('evidence-schema', 'Each claim requires id, nonempty quote, level and evidence array.')
            continue
        cid = claim['id']
        if cid in ids: add('evidence-schema', 'Duplicate claim id: ' + cid)
        ids.add(cid)
        if claim['quote'] not in text: add('claim-not-found', cid + ': exact quote absent from README.')
        if not claim['evidence'] and claim['level'] != 'unknown':
            add('evidence-missing', cid + ': a known level requires evidence.')
        for item in claim['evidence']:
            if not isinstance(item, dict) or not isinstance(item.get('path'), str) or not isinstance(item.get('excerpt'), str) or not item.get('excerpt'):
                add('evidence-schema', cid + ': evidence requires relative path and nonempty excerpt.')
                continue
            path = Path(item['path'])
            if path.is_absolute() or not (root/path).resolve().is_relative_to(root):
                add('evidence-path', cid + ': evidence path must stay inside root.')
                continue
            actual, wrong = case_path(root/path)
            if not actual or not actual.is_file():
                add('evidence-missing', cid + ': missing evidence file: ' + str(path))
                continue
            if wrong: add('path-case', cid + ': incorrect evidence path case: ' + str(path))
            try: content = actual.read_bytes()
            except OSError:
                add('read-error', cid + ': evidence unreadable: ' + str(path))
                continue
            if item['excerpt'] not in content.decode('utf-8', errors='replace'):
                add('evidence-excerpt', cid + ': excerpt absent from ' + str(path))
            if 'sha256' in item and item['sha256'] != hashlib.sha256(content).hexdigest():
                add('evidence-drift', cid + ': evidence hash changed: ' + str(path))
        if not isinstance(claim.get('reasoning'), str) or not claim.get('reasoning', '').strip():
            add('evidence-reasoning', cid + ': add a human-readable explanation of scope.', severity='warning')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('readme', nargs='?', default='README.md', type=Path)
    parser.add_argument('--root', type=Path, help='Repository root; defaults to README parent.')
    parser.add_argument('--repo', help='Expected GitHub owner/repo; otherwise use origin.')
    parser.add_argument('--allow-badge-repo', action='append', default=[], help='Explicitly permit a third-party badge owner/repo.')
    parser.add_argument('--evidence', type=Path, help='Claim/evidence JSON file.')
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as failures.')
    parser.add_argument('--ignore', action='append', default=[], help='Suppress one finding code; document the reason in review.')
    args = parser.parse_args()
    if args.repo and not re.fullmatch(r'[\w.-]+/[\w.-]+', args.repo): parser.error('--repo must be owner/repo')
    results = lint(args.readme, args.root, args.repo, args.allow_badge_repo, args.evidence)
    results = [r for r in results if r['code'] not in args.ignore]
    errors = sum(r['severity'] == 'error' for r in results)
    warnings = len(results)-errors
    if args.format == 'json':
        print(json.dumps({'file': str(args.readme), 'errors': errors, 'warnings': warnings, 'findings': results}, ensure_ascii=False, indent=2))
    else:
        for r in results: print(f"{args.readme}:{r['line']}: {r['severity']} [{r['code']}] {r['message']}")
        print(f'{errors} error(s), {warnings} warning(s). Remote availability and semantic truth are not checked.')
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main())
