#!/usr/bin/env python3
"""Run deterministic fixture/reference or candidate integrity checks; no model calls.
SPDX-License-Identifier: GPL-3.0-only
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
from validate_readme import lint


def run(root, candidates=None):
    results = []
    for case_file in sorted(root.glob('*/case.json')):
        case = json.loads(case_file.read_text())
        directory = case_file.parent
        with tempfile.TemporaryDirectory(prefix='readme-eval-') as tmp:
            work = Path(tmp)/'repo'
            shutil.copytree(directory/'fixture', work)
            baseline = lint(work/'README.md', work)
            actual = {r['code'] for r in baseline if r['severity'] == 'error'}
            checks = []
            if actual != set(case['baseline_expected_codes']):
                checks.append('Baseline diagnostics do not match expected codes.')
            source = candidates/case['id']/'README.md' if candidates else directory/'reference.md'
            ev = candidates/case['id']/'evidence.json' if candidates else directory/'reference.evidence.json'
            if not source.is_file() or not ev.is_file():
                checks.append('Missing candidate README.md or evidence.json.')
                findings = []
            else:
                shutil.copy2(source, work/'README.md')
                findings = lint(work/'README.md', work, evidence=ev)
                try:
                    claims = json.loads(ev.read_text()).get('claims', [])
                    ids = {x.get('id') for x in claims if isinstance(x, dict)}
                except (ValueError, AttributeError):
                    ids = set()
                if not set(case['required_claim_ids']).issubset(ids):
                    checks.append('Required claim IDs are missing.')
            results.append({'case':case['id'], 'mode':'candidate' if candidates else 'reference',
                            'automated_pass':not checks and not findings, 'errors':checks,
                            'findings':findings, 'semantic_review':'not_run', 'rubric':case['rubric']})
    if not results: raise ValueError('No evaluation cases found.')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evals', type=Path, default=Path(__file__).resolve().parents[1]/'evals')
    parser.add_argument('--candidates', type=Path, help='Root containing CASE/README.md and CASE/evidence.json')
    parser.add_argument('--output', type=Path, help='Optional JSON report path')
    args = parser.parse_args()
    try: results = run(args.evals, args.candidates)
    except (OSError, ValueError) as exc: parser.error(str(exc))
    report = {'schema_version':1,'model_invoked':False,'results':results}
    encoded = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    for result in results:
        print(('PASS' if result['automated_pass'] else 'FAIL') + ' ' + result['case'] + ' (' + result['mode'] + '; semantic review not run)')
        for message in result['errors']: print('  '+message)
        for finding in result['findings']: print('  '+finding['code']+': '+finding['message'])
    return 0 if all(r['automated_pass'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
