"""Checks the evaluation runner's failure reporting, not model quality."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from run_evals import run


class EvaluationRunnerTests(unittest.TestCase):
    def test_reference_suite_is_integrity_only(self):
        results = run(ROOT/'evals')
        self.assertEqual(len(results), 7)
        self.assertTrue(all(r['automated_pass'] for r in results))
        self.assertTrue(all(r['semantic_review'] == 'not_run' for r in results))

    def test_missing_candidate_is_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = run(ROOT/'evals', Path(tmp))
        self.assertTrue(all(not r['automated_pass'] for r in results))

    def test_edited_claim_does_not_silently_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for case in (ROOT/'evals').glob('*/case.json'):
                destination = root/case.parent.name
                destination.mkdir()
                shutil.copy2(case.parent/'reference.md', destination/'README.md')
                shutil.copy2(case.parent/'reference.evidence.json', destination/'evidence.json')
            evidence = json.loads((root/'ios-app/evidence.json').read_text())
            readme = root/'ios-app/README.md'
            readme.write_text(readme.read_text().replace(evidence['claims'][0]['quote'], '已验证所有设备完全兼容。'))
            results = run(ROOT/'evals', root)
            changed = next(r for r in results if r['case'] == 'ios-app')
            self.assertFalse(changed['automated_pass'])
            self.assertIn('claim-not-found', {r['code'] for r in changed['findings']})
            self.assertEqual(sum(r['automated_pass'] for r in results), 6)

    def test_empty_eval_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): run(Path(tmp))


if __name__ == '__main__':
    unittest.main()
