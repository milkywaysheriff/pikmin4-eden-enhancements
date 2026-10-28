#!/usr/bin/env python3
"""Publish this reviewed repository and its prerelease with GitHub CLI.

Use --check for a local audit without network access or publication.
No token is read or printed by this script; gh handles authentication.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'milkywaysheriff/pikmin4-eden-enhancements'
TAG = 'v1.0.0-beta.1'
TITLE = 'Pikmin 4 1.1.1 - Eden Enhancements 1.0 beta 1'
STEM = 'Pikmin4_1.1.1_Eden_Enhancements_1.0-beta1'
ASSETS = (STEM + '.zip', STEM + '_Sources.zip', 'SHA256SUMS.txt', STEM + '_checks.json')


class PublishError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise PublishError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Publisher:
    def __init__(self, root=ROOT, runner=subprocess.run):
        self.root, self.runner = Path(root), runner

    def call(self, args, check=True):
        result = self.runner(args, cwd=self.root, capture_output=True, text=True, check=False)
        if check and result.returncode:
            raise PublishError(result.stderr.strip() or result.stdout.strip() or 'Command failed: ' + args[0])
        return result

    def api(self, endpoint, missing=False):
        result = self.call(['gh', 'api', endpoint], check=False)
        if result.returncode:
            if missing and ('HTTP 404' in result.stderr or '"status":"404"' in result.stdout):
                return None
            raise PublishError(result.stderr.strip() or 'GitHub API request failed')
        return json.loads(result.stdout)

    def state(self, phase, **extra):
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
        require(self.call(['git', 'branch', '--show-current']).stdout.strip() == 'main', 'Expected main branch')
        commit = self.call(['git', 'rev-parse', 'HEAD']).stdout.strip()
        self.call([sys.executable, 'tools/build_release.py'])
        for name in ASSETS:
            require((self.root / 'dist' / name).is_file(), 'Missing release attachment: ' + name)
        return commit

    def ensure_repository(self, commit):
        profile = self.api('user')
        require(profile['login'].lower() == REPO.split('/')[0].lower(),
                'GitHub CLI is authenticated as a different account; expected milkywaysheriff')
        remote = self.api('repos/' + REPO, missing=True)
        if remote is None:
            self.call(['gh', 'repo', 'create', REPO, '--public', '--disable-wiki', '--description',
                       'Pikmin 4 1.1.1 Eden patches: FPS, Pikmin timing, camera, ultrawide and graphics options.'])
            remote = self.api('repos/' + REPO)
        require(not remote['private'] and remote['full_name'].lower() == REPO.lower(),
                'Existing repository is private or does not match; no visibility change will be made')
        empty = json.loads(self.call(['gh', 'repo', 'view', REPO, '--json', 'isEmpty']).stdout)['isEmpty']
        refs = [] if empty else self.api('repos/' + REPO + '/git/matching-refs/heads')
        require(not refs or all(r['ref'] == 'refs/heads/main' and r['object']['sha'] == commit for r in refs),
                'Existing remote has different history; it will not be overwritten')
        url = 'https://github.com/' + REPO + '.git'
        origin = self.call(['git', 'remote', 'get-url', 'origin'], check=False)
        if origin.returncode:
            self.call(['git', 'remote', 'add', 'origin', url])
        else:
            require(origin.stdout.strip() == url, 'Unexpected origin remote')
        self.state('repository_ready', commit=commit)
        # Authentication stays in gh; do not change the user's global Git configuration.
        self.call(['git', '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential',
                   'push', 'origin', 'HEAD:refs/heads/main'])
        remote_ref = self.api('repos/' + REPO + '/git/ref/heads/main')
        require(remote_ref['object']['sha'] == commit, 'Remote main differs after push')
        self.state('commit_pushed', commit=commit)

    def release(self):
        releases = self.api('repos/' + REPO + '/releases?per_page=100')
        found = [r for r in releases if r['tag_name'] == TAG]
        require(len(found) <= 1, 'Duplicate release tag')
        return found[0] if found else None

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
        self.ensure_repository(commit)
        self.verify_tag(commit)
        release = self.release()
        if release is None:
            self.call(['gh', 'release', 'create', TAG, '--repo', REPO, '--target', commit,
                       '--title', TITLE, '--notes-file', 'docs/RELEASE_NOTES.md',
                       '--draft', '--prerelease', '--latest=false'])
            release = self.release()
        require(release is not None and release['prerelease'], 'Expected prerelease was not found')
        if release['draft']:
            require(release['target_commitish'] == commit, 'Existing draft targets a different commit')
        else:
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
            self.call(['gh', 'release', 'edit', TAG, '--repo', REPO, '--draft=false', '--prerelease', '--latest=false'])
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
    args = parser.parse_args()
    publisher = Publisher()
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
