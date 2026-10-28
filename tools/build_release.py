#!/usr/bin/env python3
"""Build portable patch-only downloads from a pinned, explicit allowlist.

No Eden/profile/dump access, network requests or automatic installation.
Also works from the separately extracted Sources archive (Python stdlib).
"""
import hashlib
import itertools
import json
from pathlib import Path
import re
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
OUT = ROOT / 'dist'
STEM = 'Pikmin4_1.1.1_Eden_Enhancements_1.0-beta1'
PREFIX = STEM + '/'
GROUPS = {'fps': '01_FPS_choose_one', 'timing': '02_Timing',
          'camera': '03_Camera_choose_one', 'ultrawide': '04_Ultrawide_choose_one',
          'optional': '05_Optional'}
DOC_NAMES = ('README_EN.md', 'LEGGIMI_IT.md', 'CREDITS.md', 'VERIFICATION.md', 'SOURCE_NOTES.md')
HELPERS = ('follow_progress_delta_A38', 'movement_delta_A40', 'timers_delta_A41',
           'no_chromatic_A42', 'ultrawide_split_A45')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(relative):
    path = ROOT / relative
    require(not path.is_symlink() and path.resolve().is_relative_to(ROOT), 'Unsafe input: ' + relative)
    return path.read_bytes()


def parse_patch(data):
    """Reject unsupported syntax rather than silently dropping directives."""
    bid, mapping, enabled, stopped = None, {}, False, False
    for line in data.decode('utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith(('#', '//')):
            continue
        if re.fullmatch(r'@nsobid-[0-9A-Fa-f]{32,64}', line):
            require(bid is None, 'Duplicate build ID')
            bid = line[8:].upper()
        elif line in ('@flag print_values', '@flag offset_shift 0x100'):
            pass
        elif line == '@enabled':
            require(not enabled and not stopped, 'Multiple patch sections')
            enabled = True
        elif line == '@stop':
            require(enabled, 'Unexpected stop')
            enabled, stopped = False, True
        else:
            match = re.fullmatch(r'([0-9A-Fa-f]{8}) ([0-9A-Fa-f]+)', line)
            require(enabled and match is not None, 'Unsupported patch line: ' + line)
            address = int(match[1], 16)
            block = bytes.fromhex(match[2])
            require(address % 4 == 0 and len(block) % 4 == 0, 'Unaligned patch')
            for i, value in enumerate(block):
                require(address + i not in mapping, 'Duplicate patch address')
                mapping[address + i] = value
    require(bid and mapping and stopped and not enabled, 'Incomplete patch')
    require(len(bid) in (32, 64), 'Unexpected build ID length')
    return bid, mapping


def render(bid, mapping, label):
    lines = ['@nsobid-' + bid, '', '# Pikmin 4 1.1.1 - ' + label,
             '# gallongg - Eden Enhancements 1.0-beta1. See CREDITS.md and VERIFICATION.md.',
             '@flag print_values', '@flag offset_shift 0x100', '', '@enabled']
    for address in sorted(mapping)[::4]:
        lines.append(f'{address:08X} ' + bytes(mapping[address + i] for i in range(4)).hex().upper())
    return ('\n'.join(lines) + '\n@stop\n').encode()


def build_contents():
    catalog = json.loads(read('docs/catalog.json'))
    files = {name: read('docs/' + name) for name in DOC_NAMES}
    records, maps = [], {}
    for mod in catalog['mods']:
        record = {key: mod[key] for key in ('id', 'group', 'folder', 'notes')}
        record['files'], maps[mod['id']] = [], {}
        for source in mod['files']:
            original = read(source['source'])
            require(sha(original) == source['sha256'], 'Source hash differs: ' + source['source'])
            bid, mapping = parse_patch(original)
            expected = catalog['sdk_build_id'] if source['name'].endswith('_sdk.pchtxt') else catalog['main_build_id']
            require(bid == expected, 'Wrong executable build ID')
            before = mapping.copy()
            if mod['group'] == 'ultrawide':
                address = 0x62f0d40
                old_literal = ('5120x2160f\0').encode('utf-16le').ljust(24, b'\0')
                require(bytes(mapping[address + i] for i in range(24)) == old_literal, 'A45 base string differs')
                literal = (mod['variant'] + 'f\0').encode('utf-16le').ljust(24, b'\0')
                require(len(literal) == 24, 'Invalid viewport string')
                mapping.update({address + i: v for i, v in enumerate(literal)})
                require(all(mapping[a] == v for a, v in before.items() if not address <= a < address + 24),
                        'Viewport variant changes code')
            result = render(bid, mapping, mod['folder'])
            require(parse_patch(result) == (bid, mapping), 'Round-trip changes payload')
            if mod['id'] != 'uw3440x1440':
                require(mapping == before, 'Unexpected payload change')
            relative = GROUPS[mod['group']] + '/' + mod['folder'] + '/exefs/' + source['name']
            require(relative not in files, 'Duplicate output path')
            files[relative] = result
            record['files'].append({'path': relative, 'sha256': sha(result),
                                    'input_sha256': source['sha256'], 'build_id': bid,
                                    'patch_bytes': len(mapping)})
            maps[mod['id']][bid] = mapping
        records.append(record)
    # Enumerate valid selections. Timing is required with each unlocked FPS
    # option; optional graphics can be combined without byte-level overlap.
    choices = lambda group: [None] + [m['id'] for m in catalog['mods'] if m['group'] == group]
    combinations = 0
    for fps, camera, uw, ca, dr in itertools.product(choices('fps'), choices('camera'),
                                                   choices('ultrawide'), (False, True), (False, True)):
        selection = [v for v in (fps, camera, uw, 'timing' if fps else None,
                                  'no-ca' if ca else None, 'dr-lock' if dr else None) if v]
        used = {}
        for id in selection:
            for bid, mapping in maps[id].items():
                common = used.setdefault(bid.ljust(64, '0'), set())
                require(not common.intersection(mapping), 'Patch conflict in ' + ', '.join(selection))
                common.update(mapping)
        combinations += 1
    require(combinations == 288, 'Unexpected variant coverage')
    require(maps['uw3440x1440'][catalog['main_build_id']] != maps['uw5120x2160'][catalog['main_build_id']],
            'Viewport variants are identical')
    manifest = {key: catalog[key] for key in ('publisher', 'package_version', 'title_id', 'update',
                                            'main_build_id', 'sdk_build_id')}
    manifest.update(mods=records, byte_compatibility_combinations=combinations,
                    validation='Patch syntax, pinned inputs, payload equivalence and byte overlap checks only; not gameplay.')
    files['MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    # Protect against accidental inclusion of personal profiles and game data.
    for name, data in files.items():
        require(Path(name).suffix in ('.md', '.pchtxt', '.json'), 'Unexpected payload file')
        require(not re.search(rb'/home/[A-Za-z0-9_.-]+/', data), 'Private path in download')
        require(not any(part in ('..', 'reports', 'romfs') for part in Path(name).parts), 'Unexpected payload directory')
    files['SHA256SUMS.txt'] = ''.join(f'{sha(data)}  {name}\n' for name, data in sorted(files.items())).encode()
    return catalog, files, manifest


def write_zip(path, prefix, files):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(prefix + name, date_time=(2026, 10, 28, 0, 0, 0))
            info.compress_type, info.external_attr = zipfile.ZIP_DEFLATED, 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, 'ZIP CRC failure')
        require(len(archive.namelist()) == len(files), 'Unexpected ZIP contents')
        with tempfile.TemporaryDirectory() as tmp:
            archive.extractall(tmp)
            for name, data in files.items():
                require((Path(tmp) / (prefix + name)).read_bytes() == data, 'Extraction mismatch')
    path.with_suffix('.zip.sha256').write_text(sha(path.read_bytes()) + '  ' + path.name + '\n')


def main():
    catalog, files, manifest = build_contents()
    OUT.mkdir(exist_ok=True)
    download = OUT / (STEM + '.zip')
    write_zip(download, PREFIX, files)
    source_names = {'.gitignore', '.release-files.json', 'README.md',
                    '.github/workflows/verify.yml', 'tests/test_publication.py',
                    'tools/build_release.py', 'tools/verify_sources.py', 'tools/publish_github.py',
                    'docs/catalog.json', 'docs/RELEASE_NOTES.md'}
    source_names.update('docs/' + name for name in DOC_NAMES)
    source_names.update(source['source'] for mod in catalog['mods'] for source in mod['files'])
    source_names.update('sources/' + stem + suffix for stem in HELPERS for suffix in ('.S', '.ld'))
    source_files = {name: read(name) for name in sorted(source_names)}
    for name, data in source_files.items():
        require(name == '.gitignore' or Path(name).suffix in ('.S', '.ld', '.py', '.pchtxt', '.json', '.md', '.yml'), 'Unexpected source file')
        require(not re.search(rb'/home/[A-Za-z0-9_.-]+/', data), 'Private path in sources')
    sources = OUT / (STEM + '_Sources.zip')
    write_zip(sources, STEM + '_Sources/', source_files)
    report = {'status': 'pass', 'mod_choices': len(manifest['mods']),
              'patch_files': sum(len(m['files']) for m in manifest['mods']),
              'byte_compatibility_combinations': manifest['byte_compatibility_combinations'],
              'checks': ['Pinned input SHA256', 'Strict syntax/build IDs', 'Re-encoded payload equivalence',
                         'A45 1440 variant differs only in viewport string', 'No cross-feature byte overlap',
                         'Explicit patch/docs/source allowlists', 'No private host paths', 'ZIP CRC and extraction'],
              'archives': [{'file': p.name, 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
                           for p in (download, sources)],
              'gameplay': 'No new game run. See VERIFICATION.md for scoped user feedback.'}
    (OUT / (STEM + '_checks.json')).write_text(json.dumps(report, indent=2) + '\n')
    checksum_names = (STEM + '.zip', STEM + '_Sources.zip', STEM + '_checks.json')
    (OUT / 'SHA256SUMS.txt').write_text(''.join(
        sha((OUT / name).read_bytes()) + '  ' + name + '\n' for name in checksum_names))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
