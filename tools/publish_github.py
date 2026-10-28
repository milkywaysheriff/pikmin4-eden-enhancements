#!/usr/bin/env python3
"""Publish this reviewed repository and its prerelease with GitHub CLI.

Use --check for a local audit without network access or publication.
No token is read or printed by this script; gh handles authentication.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'milkywaysheriff/pikmin4-eden-enhancements'
TAG = 'v1.0.0-beta.1'
TITLE = 'Pikmin 4 1.1.1 - Eden Enhancements 1.0 beta 1'
DESCRIPTION = 'Optional FPS, camera, ultrawide and graphics mods for Pikmin 4 1.1.1 on Eden.'
STEM = 'Pikmin4_1.1.1_Eden_Enhancements_1.0-beta1'
ASSETS = (STEM + '.zip', STEM + '_Sources.zip', 'SHA256SUMS.txt', STEM + '_checks.json')
LEGACY_NOTES_SHA = '0fcef4b226775f041d726c3f953b4e234b04ded1aaaaca86dc1a250d71d18d7d'


class PublishError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise PublishError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Publisher:
    def __init__(self, root=ROOT, runner=subprocess.run, ci=False):
        self.root, self.runner = Path(root), runner
        self.ci = ci
        self.release_id = None
        path = self.root / '.publish-state.json'
        if path.is_file():
            state = json.loads(path.read_text())
            if state.get('repository') == REPO and state.get('tag') == TAG:
                self.release_id = state.get('release_id')

    def call(self, args, check=True, input_text=None):
        options = {'input': input_text} if input_text is not None else {}
        result = self.runner(args, cwd=self.root, capture_output=True, text=True, check=False, **options)
        if check and result.returncode:
            raise PublishError(result.stderr.strip() or result.stdout.strip() or 'Command failed: ' + args[0])
        return result

    def api(self, endpoint, missing=False, payload=None, method=None):
        args = ['gh', 'api', endpoint]
        if payload is not None:
            args += ['--method', method or 'POST', '--input', '-']
        result = self.call(args, check=False, input_text=json.dumps(payload) if payload is not None else None)
        if result.returncode:
            if missing and ('HTTP 404' in result.stderr or '"status":"404"' in result.stdout):
                return None
            raise PublishError(result.stderr.strip() or 'GitHub API request failed')
        return json.loads(result.stdout)

    def state(self, phase, **extra):
        if self.release_id is not None:
            extra.setdefault('release_id', self.release_id)
        (self.root / '.publish-state.json').write_text(json.dumps(
            {'phase': phase, 'repository': REPO, 'tag': TAG, **extra}, indent=2) + '\n')

    def audit(self):
        manifest = json.loads((self.root / '.release-files.json').read_text())
        expected = set(manifest) | {'.release-files.json'}
        tracked = set(self.call(['git', 'ls-files', '-z']).stdout.rstrip('\0').split('\0'))
        require(tracked == expected, 'Tracked files differ from the reviewed publication allowlist')
        require(not self.call(['git', 'status', '--porcelain', '--untracked-files=all']).stdout.strip(),
                'Repository has unreviewed changes; publication stopped')
        for name, digest in manifest.items():
            path = self.root / name
            require(not path.is_symlink() and path.resolve().is_relative_to(self.root.resolve()), 'Unsafe file path')
            require(sha(path.read_bytes()) == digest, 'Reviewed file changed: ' + name)
        commit = self.call(['git', 'rev-parse', 'HEAD']).stdout.strip()
        if self.ci:
            self.check_ci(commit)
        else:
            require(self.call(['git', 'branch', '--show-current']).stdout.strip() == 'main', 'Expected main branch')
        self.call([sys.executable, 'tools/build_release.py'])
        for name in ASSETS:
            require((self.root / 'dist' / name).is_file(), 'Missing release attachment: ' + name)
        return commit

    def ensure_repository(self, commit):
        if self.ci:
            self.check_ci(commit)
        else:
            profile = self.api('user')
            require(profile['login'].lower() == REPO.split('/')[0].lower(),
                    'GitHub CLI is authenticated as a different account; expected milkywaysheriff')
        remote = self.api('repos/' + REPO, missing=True)
        if remote is None:
            require(not self.ci, 'CI must use the existing repository')
            self.call(['gh', 'repo', 'create', REPO, '--public', '--disable-wiki', '--description',
                       DESCRIPTION])
            remote = self.api('repos/' + REPO)
        require(not remote['private'] and remote['full_name'].lower() == REPO.lower(),
                'Existing repository is private or does not match; no visibility change will be made')
        empty = json.loads(self.call(['gh', 'repo', 'view', REPO, '--json', 'isEmpty']).stdout)['isEmpty']
        refs = [] if empty else self.api('repos/' + REPO + '/git/matching-refs/heads')
        require(not refs or all(r['ref'] == 'refs/heads/main' and self.is_ancestor(r['object']['sha'], commit) for r in refs),
                'Existing remote has different history; it will not be overwritten')
        url = 'https://github.com/' + REPO + '.git'
        origin = self.call(['git', 'remote', 'get-url', 'origin'], check=False)
        if origin.returncode:
            self.call(['git', 'remote', 'add', 'origin', url])
        else:
            require(origin.stdout.strip().removesuffix('.git') == url.removesuffix('.git'), 'Unexpected origin remote')
        self.state('repository_ready', commit=commit)
        # Authentication stays in gh; do not change the user's global Git configuration.
        if not refs or refs[0]['object']['sha'] != commit:
            self.call(['git', '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential',
                       'push', 'origin', 'HEAD:refs/heads/main'])
        remote_ref = self.api('repos/' + REPO + '/git/ref/heads/main')
        require(remote_ref['object']['sha'] == commit, 'Remote main differs after push')
        self.state('commit_pushed', commit=commit)
        if not self.ci:
            self.call(['gh', 'repo', 'edit', REPO, '--description', DESCRIPTION])

    @staticmethod
    def check_ci(commit):
        require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == REPO
                and os.environ.get('GITHUB_REF') == 'refs/heads/main' and os.environ.get('GITHUB_SHA') == commit,
                'CI publication is restricted to this repository main commit')

    def is_ancestor(self, previous, commit):
        return (isinstance(previous, str) and re.fullmatch(r'[0-9a-f]{40}', previous) is not None
                and self.call(['git', 'merge-base', '--is-ancestor', previous, commit], check=False).returncode == 0)

    def release(self):
        # gh resolves pending draft tag names with GraphQL; REST list/tag
        # lookups can miss them. Once known, keep the numeric ID across runs.
        if self.release_id is None:
            result = self.call(['gh', 'release', 'view', TAG, '--repo', REPO,
                                '--json', 'databaseId,tagName'], check=False)
            if result.returncode:
                require('release not found' in result.stderr.lower(), result.stderr.strip() or 'Release lookup failed')
                releases = self.api('repos/' + REPO + '/releases?per_page=100')
                # Recover the earlier publisher's draft even if GitHub has
                # not attached the pending tag. Require its exact notes,
                # title, empty assets and our reviewed ancestor commit.
                matches = [r for r in releases if r['tag_name'] == TAG or (
                    r['draft'] and self.placeholder_tag(r['tag_name']) and r.get('name') == TITLE
                    and not r['assets'] and sha(r.get('body', '').encode()) == LEGACY_NOTES_SHA
                    and self.is_ancestor(r['target_commitish'], self.commit))]
                require(len(matches) <= 1, 'Several matching release drafts found; no duplicate will be created')
                if not matches:
                    return None
                self.release_id = matches[0]['id']
            else:
                found = json.loads(result.stdout)
                require(found['tagName'] == TAG or self.placeholder_tag(found['tagName']), 'Unexpected release tag')
                self.release_id = found['databaseId']
        require(type(self.release_id) is int and self.release_id > 0, 'Invalid release ID')
        release = self.api('repos/' + REPO + '/releases/' + str(self.release_id))
        require(release['tag_name'] == TAG or (release['draft'] and self.placeholder_tag(release['tag_name'])),
                'Saved release ID belongs to another tag')
        return release

    @staticmethod
    def placeholder_tag(tag):
        return tag == '' or (isinstance(tag, str) and tag.startswith('untagged-'))

    def verify_existing_assets(self, release):
        existing = {a['name']: a for a in release['assets']}
        require(set(existing) <= set(ASSETS), 'Unexpected attachments on existing release')
        with tempfile.TemporaryDirectory() as tmp:
            for name in sorted(existing):
                self.call(['gh', 'release', 'download', TAG, '--repo', REPO, '--pattern', name, '--dir', tmp])
                require(sha((Path(tmp) / name).read_bytes()) == sha((self.root / 'dist' / name).read_bytes()),
                        'Remote attachment differs and will not be overwritten: ' + name)
        return existing

    def verify_tag(self, commit):
        ref = self.api('repos/' + REPO + '/git/ref/tags/' + TAG, missing=True)
        if ref is None:
            return False
        obj = ref['object']
        for _ in range(5):
            if obj['type'] != 'tag':
                break
            obj = self.api('repos/' + REPO + '/git/tags/' + obj['sha'])['object']
        require(obj['type'] == 'commit' and obj['sha'] == commit,
                'Release tag points at a different commit; it will not be moved')
        return True

    def publish(self, commit):
        self.commit = commit
        self.ensure_repository(commit)
        self.verify_tag(commit)
        release = self.release()
        if release is None:
            release = self.api('repos/' + REPO + '/releases', payload={
                'tag_name': TAG, 'target_commitish': commit, 'name': TITLE,
                'body': (self.root / 'docs/RELEASE_NOTES.md').read_text(),
                'draft': True, 'prerelease': True, 'make_latest': 'false'})
            self.release_id = release['id']
            self.state('draft_created', commit=commit)
        require(release is not None and (release['tag_name'] == TAG or
                (release['draft'] and self.placeholder_tag(release['tag_name']))), 'Expected release was not found')
        if release['draft']:
            previous = release['target_commitish']
            if previous != commit:
                require(not release['assets'] and self.is_ancestor(previous, commit),
                        'Existing draft has different files or unrelated history; it will not be retargeted')
            if not self.verify_tag(commit):
                self.api('repos/' + REPO + '/git/refs', payload={'ref': 'refs/tags/' + TAG, 'sha': commit})
                require(self.verify_tag(commit), 'Release tag creation failed')
            release = self.api('repos/' + REPO + '/releases/' + str(self.release_id), method='PATCH', payload={
                'tag_name': TAG, 'target_commitish': commit, 'name': TITLE,
                'body': (self.root / 'docs/RELEASE_NOTES.md').read_text(), 'prerelease': True})
            require(release['draft'] and release['prerelease'] and release['target_commitish'] == commit,
                    'Draft update verification failed')
        else:
            require(release['prerelease'], 'An existing published release is not a prerelease')
            require(self.verify_tag(commit), 'Published release has no matching tag')
        self.state('release_prepared', commit=commit, release_id=release['id'])
        existing = self.verify_existing_assets(release)
        missing = [str(self.root / 'dist' / name) for name in ASSETS if name not in existing]
        if missing:
            self.call(['gh', 'release', 'upload', TAG, '--repo', REPO, *missing])
        release = self.release()
        require(set(self.verify_existing_assets(release)) == set(ASSETS), 'Incomplete attachment upload')
        self.state('attachments_verified', commit=commit, release_id=release['id'])
        if release['draft']:
            self.api('repos/' + REPO + '/releases/' + str(self.release_id), method='PATCH', payload={
                'tag_name': TAG, 'target_commitish': commit, 'draft': False, 'prerelease': True, 'make_latest': 'false'})
        release = self.release()
        require(not release['draft'] and release['prerelease'], 'Prerelease is not published')
        require(self.verify_tag(commit), 'Published tag verification failed')
        require(set(self.verify_existing_assets(release)) == set(ASSETS), 'Published attachments incomplete')
        self.state('published_verified', commit=commit, release_url=release['html_url'],
                   assets={name: sha((self.root / 'dist' / name).read_bytes()) for name in ASSETS})
        print('Repository: https://github.com/' + REPO)
        print('Release:', release['html_url'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Local audit/build only; no GitHub access')
    parser.add_argument('--ci', action='store_true', help='Use this repository main workflow token')
    args = parser.parse_args()
    publisher = Publisher(ci=args.ci)
    try:
        commit = publisher.audit()
        if args.check:
            print('Local publication audit passed:', commit)
        else:
            publisher.publish(commit)
    except (PublishError, OSError, KeyError, ValueError) as error:
        raise SystemExit(str(error)) from None


if __name__ == '__main__':
    main()
