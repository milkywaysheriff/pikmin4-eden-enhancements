"""Offline release integrity and publication failure/resume checks."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_release as build
import publish_github as publish

COMMIT = 'a' * 40


class FakeGitHub(publish.Publisher):
    """In-memory remote: no network, credentials or real GitHub mutations."""
    def __init__(self, root):
        super().__init__(root)
        self.login, self.exists, self.refs = 'milkywaysheriff', False, []
        self.remote_release, self.tag, self.origin = None, None, None
        self.uploads, self.actions = [], []
        self.fail_upload = False
        self.placeholder_draft = False
        self.create_count = 0
        self.api_requests = []
        self.ancestors = {(COMMIT, COMMIT)}
        (self.root / 'docs').mkdir()
        (self.root / 'docs/RELEASE_NOTES.md').write_text('Public release notes')
        (self.root / 'dist').mkdir()
        for name in publish.ASSETS:
            (self.root / 'dist' / name).write_bytes(('test:' + name).encode())

    def api(self, path, missing=False, payload=None, method=None):
        self.api_requests.append((path, payload, method))
        if path.endswith('/git/refs') and payload is not None:
            self.tag = payload['sha']
            return {'object': {'type': 'commit', 'sha': self.tag}}
        if path.endswith('/releases') and payload is not None:
            self.create_count += 1
            self.remote_release = {'id': 1, 'tag_name': '' if self.placeholder_draft else payload['tag_name'],
                                   'name': payload['name'], 'body': payload['body'],
                                   'draft': payload['draft'], 'prerelease': payload['prerelease'],
                                   'target_commitish': payload['target_commitish'], 'assets': [],
                                   'html_url': 'https://github.com/' + publish.REPO + '/releases/tag/' + publish.TAG}
            return self.remote_release
        if path.endswith('/releases/1'):
            if payload is not None: self.remote_release.update(payload)
            return self.remote_release
        if path == 'user': return {'login': self.login}
        if path == 'repos/' + publish.REPO:
            return {'private': False, 'full_name': publish.REPO} if self.exists else None
        if '/git/matching-refs/heads' in path: return self.refs
        if '/git/ref/heads/main' in path: return {'object': {'sha': self.refs[0]['object']['sha']}}
        if '/releases?' in path: return [] if self.remote_release is None else [self.remote_release]
        if '/git/ref/tags/' in path:
            return None if self.tag is None else {'object': {'type': 'commit', 'sha': self.tag}}
        raise AssertionError(path)

    def call(self, args, check=True, input_text=None):
        self.actions.append(args)
        output, code = '', 0
        if args[:3] == ['gh', 'repo', 'create']: self.exists = True
        elif args[:3] == ['gh', 'repo', 'edit']: pass
        elif args[:3] == ['gh', 'repo', 'view']: output = json.dumps({'isEmpty': not self.refs})
        elif args[:3] == ['gh', 'release', 'view']:
            if self.remote_release is None:
                return subprocess.CompletedProcess(args, 1, '', 'release not found')
            output = json.dumps({'databaseId': self.remote_release['id'], 'tagName': self.remote_release['tag_name']})
        elif args[:3] == ['git', 'merge-base', '--is-ancestor']:
            code = 0 if (args[3], args[4]) in self.ancestors else 1
        elif args[:4] == ['git', 'remote', 'get-url', 'origin']:
            output, code = self.origin or '', 0 if self.origin else 1
        elif args[:4] == ['git', 'remote', 'add', 'origin']: self.origin = args[4]
        elif args[0] == 'git' and 'push' in args:
            self.refs = [{'ref': 'refs/heads/main', 'object': {'sha': COMMIT}}]
        elif args[:3] == ['gh', 'release', 'upload']:
            for filename in args[6:]:
                path = Path(filename)
                if any(a['name'] == path.name for a in self.remote_release['assets']):
                    raise AssertionError('Duplicate upload')
                self.remote_release['assets'].append({'name': path.name, 'bytes': path.read_bytes()})
                self.uploads.append(path.name)
                if self.fail_upload:
                    self.fail_upload = False
                    raise publish.PublishError('Simulated interrupted upload')
        elif args[:3] == ['gh', 'release', 'download']:
            name, directory = args[args.index('--pattern') + 1], Path(args[args.index('--dir') + 1])
            data = next(a['bytes'] for a in self.remote_release['assets'] if a['name'] == name)
            (directory / name).write_bytes(data)
        else: raise AssertionError(args)
        return subprocess.CompletedProcess(args, code, output, '')


class PublicationTests(unittest.TestCase):
    def scenario(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return FakeGitHub(Path(tmp.name))

    def test_success_requires_verified_assets_and_published_tag(self):
        remote = self.scenario()
        with contextlib.redirect_stdout(io.StringIO()): remote.publish(COMMIT)
        self.assertFalse(remote.remote_release['draft'])
        self.assertTrue(remote.remote_release['prerelease'])
        self.assertEqual(set(remote.uploads), set(publish.ASSETS))
        self.assertEqual(remote.tag, COMMIT)
        self.assertEqual(json.loads((remote.root / '.publish-state.json').read_text())['phase'], 'published_verified')

    def test_wrong_account_does_not_create_repository(self):
        remote = self.scenario(); remote.login = 'someone-else'
        with self.assertRaises(publish.PublishError): remote.publish(COMMIT)
        self.assertFalse(remote.exists)
        self.assertEqual(remote.actions, [])

    def test_existing_remote_history_is_never_overwritten(self):
        remote = self.scenario(); remote.exists = True
        remote.refs = [{'ref': 'refs/heads/main', 'object': {'sha': 'b' * 40}}]
        with self.assertRaises(publish.PublishError): remote.publish(COMMIT)
        self.assertEqual(remote.refs[0]['object']['sha'], 'b' * 40)
        self.assertFalse(any('push' in args for args in remote.actions))

    def test_interrupted_upload_resumes_without_duplicate_assets(self):
        remote = self.scenario(); remote.fail_upload = True
        with self.assertRaises(publish.PublishError): remote.publish(COMMIT)
        self.assertTrue(remote.remote_release['draft'])
        with contextlib.redirect_stdout(io.StringIO()):
            remote.publish(COMMIT)
            remote.publish(COMMIT)
        self.assertEqual(len(remote.uploads), len(publish.ASSETS))
        self.assertEqual(len(set(remote.uploads)), len(publish.ASSETS))

    def test_changed_remote_asset_stays_intact_and_release_stays_draft(self):
        remote = self.scenario(); remote.fail_upload = True
        with self.assertRaises(publish.PublishError): remote.publish(COMMIT)
        remote.remote_release['assets'][0]['bytes'] = b'different existing content'
        with self.assertRaises(publish.PublishError): remote.publish(COMMIT)
        self.assertTrue(remote.remote_release['draft'])
        self.assertEqual(remote.remote_release['assets'][0]['bytes'], b'different existing content')

    def test_existing_tag_is_never_retargeted(self):
        remote = self.scenario(); remote.exists = True; remote.tag = 'b' * 40
        with self.assertRaises(publish.PublishError): remote.publish(COMMIT)
        self.assertEqual(remote.tag, 'b' * 40)
        self.assertIsNone(remote.remote_release)

    def test_placeholder_draft_and_empty_release_list_do_not_trigger_duplicate_creation(self):
        remote = self.scenario(); remote.placeholder_draft = True
        with contextlib.redirect_stdout(io.StringIO()):
            remote.publish(COMMIT)
            remote.publish(COMMIT)
        self.assertEqual(remote.create_count, 1)
        self.assertEqual(remote.remote_release['tag_name'], publish.TAG)
        self.assertFalse(remote.remote_release['draft'])
        self.assertEqual(sum('/releases?' in path for path, _, _ in remote.api_requests), 1)

    def test_pending_draft_without_prerelease_flag_is_reused_and_marked(self):
        remote = self.scenario(); remote.fail_upload = True
        with self.assertRaises(publish.PublishError): remote.publish(COMMIT)
        remote.remote_release['prerelease'] = False
        with contextlib.redirect_stdout(io.StringIO()): remote.publish(COMMIT)
        self.assertEqual(remote.create_count, 1)
        self.assertTrue(remote.remote_release['prerelease'])
        self.assertFalse(remote.remote_release['draft'])

    def test_reviewed_descendant_can_fast_forward_existing_main_and_empty_draft(self):
        remote = self.scenario(); remote.exists = True
        previous = 'c' * 40
        remote.ancestors.add((previous, COMMIT))
        remote.refs = [{'ref': 'refs/heads/main', 'object': {'sha': previous}}]
        remote.remote_release = {'id': 1, 'tag_name': publish.TAG, 'draft': True, 'prerelease': True,
                                 'target_commitish': previous, 'assets': [], 'html_url': 'https://example.test/release'}
        with contextlib.redirect_stdout(io.StringIO()): remote.publish(COMMIT)
        self.assertEqual(remote.create_count, 0)
        self.assertEqual(remote.remote_release['target_commitish'], COMMIT)
        self.assertFalse(remote.remote_release['draft'])

    def test_creation_persists_id_before_any_refresh_or_upload(self):
        remote = self.scenario(); remote.fail_upload = True
        with self.assertRaises(publish.PublishError): remote.publish(COMMIT)
        saved = json.loads((remote.root / '.publish-state.json').read_text())
        self.assertEqual(saved['release_id'], 1)
        self.assertEqual(remote.create_count, 1)

    def test_api_sends_actual_boolean_json_not_string_flags(self):
        received = []
        def runner(args, **kwargs):
            received.append((args, json.loads(kwargs['input'])))
            return subprocess.CompletedProcess(args, 0, '{"id": 4}', '')
        with tempfile.TemporaryDirectory() as tmp:
            client = publish.Publisher(Path(tmp), runner)
            client.api('repos/' + publish.REPO + '/releases', payload={'draft': True, 'prerelease': True})
        self.assertEqual(received[0][0][-4:], ['--method', 'POST', '--input', '-'])
        self.assertIs(received[0][1]['prerelease'], True)

    def test_public_docs_cover_features_without_private_history(self):
        for name in ('README.md', 'docs/README_EN.md', 'docs/LEGGIMI_IT.md', 'docs/RELEASE_NOTES.md', 'docs/CREDITS.md'):
            text = (ROOT / name).read_text().lower()
            self.assertNotIn('stop' + ' talking', text)
        lead = (ROOT / 'README.md').read_text().split('## Quick installation')[0]
        self.assertNotIn('Dandori', lead)
        self.assertNotIn('A45', lead)

    def test_ci_refuses_wrong_repository_before_using_token(self):
        with patch.dict('os.environ', {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'someone/else',
                                      'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': COMMIT}):
            with self.assertRaises(publish.PublishError): publish.Publisher.check_ci(COMMIT)

    def test_ci_context_accepts_only_matching_main_commit(self):
        with patch.dict('os.environ', {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': publish.REPO,
                                      'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': COMMIT}):
            publish.Publisher.check_ci(COMMIT)
            with self.assertRaises(publish.PublishError): publish.Publisher.check_ci('b' * 40)

    def test_sources_rebuild_same_downloads_and_modified_input_is_rejected(self):
        with contextlib.redirect_stdout(io.StringIO()): build.main()
        with tempfile.TemporaryDirectory() as tmp:
            import zipfile
            with zipfile.ZipFile(build.OUT / (build.STEM + '_Sources.zip')) as archive: archive.extractall(tmp)
            root = Path(tmp) / (build.STEM + '_Sources')
            subprocess.run([sys.executable, 'tools/build_release.py'], cwd=root, capture_output=True, check=True)
            for suffix in ('.zip', '_Sources.zip'):
                self.assertEqual((root / 'dist' / (build.STEM + suffix)).read_bytes(),
                                 (build.OUT / (build.STEM + suffix)).read_bytes())
            catalog = json.loads((root / 'docs/catalog.json').read_text())
            source = root / catalog['mods'][0]['files'][0]['source']
            source.write_bytes(source.read_bytes() + b'\n# edited\n')
            result = subprocess.run([sys.executable, 'tools/build_release.py'], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Source hash differs', result.stderr)


if __name__ == '__main__': unittest.main()
