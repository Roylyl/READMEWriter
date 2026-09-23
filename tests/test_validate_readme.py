"""Behavioral regression tests; no network or project commands are executed."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('validator', Path(__file__).parents[1]/'scripts/validate_readme.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class LintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.readme = self.root/'README.md'

    def check(self, body, files=None, **kwargs):
        self.readme.write_text(body)
        for path, data in (files or {}).items():
            f = self.root/path
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(data)
        return v.lint(self.readme, self.root, **kwargs)

    def codes(self, *args, **kwargs):
        return {x['code'] for x in self.check(*args, **kwargs)}

    def test_missing_files_and_images(self):
        self.assertEqual(self.codes('# App\n[x](none.md)\n![x](none.png)'), {'missing-file', 'missing-image'})

    def test_case_sensitive_on_any_filesystem(self):
        self.assertIn('path-case', self.codes('# App\n![Logo](assets/logo.svg)', {'assets/Logo.svg': '<svg/>'}))

    def test_encoded_paths_parentheses_and_titles(self):
        self.assertFalse(self.check('# App\n[x](docs/a(b).md "Title")\n[x](docs/a%20b.md)\n[x](<docs/a b.md>)', {'docs/a(b).md':'# A', 'docs/a b.md':'# B'}))

    def test_reference_images_and_links(self):
        body = '# App\n![logo][img]\n[Guide][]\n[other]\n[img]: logo.svg\n[Guide]: guide.md\n[other]: guide.md\n'
        self.assertFalse(self.check(body, {'logo.svg':'<svg/>', 'guide.md':'# Guide'}))

    def test_undefined_reference(self):
        self.assertIn('undefined-reference', self.codes('# App\n[x][missing]'))

    def test_unlinked_brackets_are_not_references(self):
        self.assertFalse(self.check('# App\n[x] [!NOTE] plain brackets'))

    def test_html_and_nested_badges(self):
        body = '<h1>App</h1>\n[![badge](https://img.shields.io/github/stars/wrong/project)](LICENSE)'
        self.assertIn('badge-repo-mismatch', self.codes(body, {'LICENSE':'license'}, expected_repo='owner/project'))

    def test_html_images_and_anchors(self):
        body = '<h1>App</h1>\n<a href="#custom">go</a><a id="custom"></a><img src="pic.svg">'
        self.assertFalse(self.check(body, {'pic.svg':'<svg/>'}))

    def test_unicode_duplicate_and_code_headings(self):
        body = '# App\n## 安装与运行\n## Usage\n## Usage\n## Usage-1\n[x](#安装与运行) [x](#usage-1) [x](#usage-1-1)\n```sh\n# fake\n[x](missing)\n```\n'
        self.assertFalse(self.check(body))

    def test_inline_code_not_a_link(self):
        self.assertFalse(self.check('# App\n`[x](missing.md)`'))

    def test_setext_h1(self):
        self.assertIn('duplicate-h1', self.codes('App\n===\n# Second\n'))

    def test_cross_file_anchor(self):
        self.assertIn('invalid-anchor', self.codes('# App\n[x](guide.md#missing)', {'guide.md':'# Guide\n## Install'}))

    def test_cross_file_html_anchor(self):
        self.assertFalse(self.check('# App\n[x](page.html#start)', {'page.html':'<section id="start"></section>'}))

    def test_duplicate_h1_html_markdown(self):
        self.assertIn('duplicate-h1', self.codes('<h1>App</h1>\n# Another'))

    def test_placeholder_even_in_examples(self):
        self.assertIn('placeholder', self.codes('# App\n```sh\nclone {{REPO}}\n```'))

    def test_local_paths_but_not_urls(self):
        self.assertIn('local-absolute-path', self.codes('# App\n```sh\ncd /Users/alice/project\n```'))
        self.assertIn('local-absolute-path', self.codes('# App\n`C:\\Users\\Alice\\repo`'))
        self.assertFalse(self.check('# App\nhttps://example.com/home/alice\n`$HOME/.codex`'))

    def test_custom_schemes_are_not_windows_paths(self):
        self.assertFalse(self.check('# App\n`chrome://extensions` `clash://install-config` `vscode://file`'))

    def test_comment_content_ignored_for_links(self):
        self.assertFalse(self.check('# App\n<!-- [x](missing) -->'))

    def test_origin_and_third_party_badges(self):
        url = 'https://img.shields.io/github/actions/workflow/status/owner/repo/ci.yml?branch=main'
        self.assertFalse(self.check('# App\n![]('+url+')', expected_repo='Owner/Repo'))
        self.assertFalse(self.check('# App\n![]('+url+')', expected_repo='another/repo', allowed_repos=['owner/repo']))
        self.assertIn('badge-repo-unverified', self.codes('# App\n![]('+url+')'))

    def test_release_badge(self):
        self.assertEqual(v.badge_repo('https://img.shields.io/github/v/release/a/b'), 'a/b')
        self.assertEqual(v.badge_repo('https://img.shields.io/github/downloads/a/b/total'), 'a/b')
        self.assertIsNone(v.badge_repo('https://img.shields.io/badge/license-MIT-blue'))

    def test_symlink_outside_root(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other)/'outside.md'
            target.write_text('# Outside')
            (self.root/'link.md').symlink_to(target)
            self.assertIn('outside-root', self.codes('# App\n[x](link.md)'))

    def test_json_cli_exit_code(self):
        self.readme.write_text('# App\n[x](missing.md)')
        run = subprocess.run([sys.executable, str(Path(v.__file__)), str(self.readme), '--format', 'json'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)['errors'], 1)

    def test_evidence_integrity_and_drift(self):
        evidence = self.root/'evidence.json'
        evidence.write_text(json.dumps({'schema_version':1,'claims':[{'id':'target','quote':'配置目标为 iOS 26。','level':'configuration','reasoning':'Configuration only.','evidence':[{'path':'app.conf','excerpt':'target=26','sha256':'0'*64}]}]}))
        self.assertEqual(self.codes('# App\n配置目标为 iOS 26。', {'app.conf':'target=26'}, evidence=evidence), {'evidence-drift'})

    def test_evidence_missing_quote_excerpt(self):
        evidence = self.root/'evidence.json'
        evidence.write_text(json.dumps({'schema_version':1,'claims':[{'id':'x','quote':'absent','level':'build','reasoning':'test','evidence':[{'path':'build.log','excerpt':'PASS'}]}]}))
        self.assertEqual(self.codes('# App', {'build.log':'FAIL'}, evidence=evidence), {'claim-not-found','evidence-excerpt'})

    def test_evidence_schema_and_path_escape(self):
        evidence = self.root/'evidence.json'
        evidence.write_text('[]')
        self.assertIn('evidence-schema', self.codes('# App', evidence=evidence))
        evidence.write_text(json.dumps({'schema_version':1,'claims':[{'id':'x','quote':'App','level':'configuration','reasoning':'test','evidence':[{'path':'../secret','excerpt':'secret'}]}]}))
        self.assertIn('evidence-path', self.codes('# App', evidence=evidence))


if __name__ == '__main__':
    unittest.main()
