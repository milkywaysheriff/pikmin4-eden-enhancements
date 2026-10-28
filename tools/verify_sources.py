#!/usr/bin/env python3
"""Reassemble the supplied new helpers with LLVM and compare patch bytes.

Only patch/source files and a temporary directory are accessed; no game
dump, emulator profile, network connection or Python dependency is needed.
"""
from pathlib import Path
import subprocess
import tempfile

from build_release import ROOT, build_contents, parse_patch, require


def main():
    _, files, manifest = build_contents()
    by_id = {mod['id']: mod for mod in manifest['mods']}
    patch_map = lambda id: parse_patch(files[by_id[id]['files'][0]['path']])[1]
    timing, ca, uw = patch_map('timing'), patch_map('no-ca'), patch_map('uw5120x2160')
    recipes = [
        ('follow_progress_delta_A38', timing, {'.delta': [0x1a3b148], '.text': [0x62f0b80]}),
        ('movement_delta_A40', timing, {'.delta2': [0x1a399e4], '.delta1': [0x1a39a18],
                                       '.progress': [0x62f0bb4], '.ride': [0x62f0e20]}),
        ('timers_delta_A41', timing, {'.timers': [0x62f0ea8],
                                     '.follow_delta': [0x135c4b8, 0x135cf94, 0x135db94, 0x1364570]}),
        ('no_chromatic_A42', ca, {'.text': [0x62f0a40]}),
        ('ultrawide_split_A45', uw, {'.text': [0x62f0c00]}),
    ]
    compared = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for stem, mapping, sections in recipes:
            source = ROOT / 'sources' / stem
            obj, elf = tmp / (stem + '.o'), tmp / (stem + '.elf')
            subprocess.run(['clang', '--target=aarch64-none-elf', '-c',
                            str(source.with_suffix('.S')), '-o', str(obj)], check=True)
            subprocess.run(['ld.lld', '-T', str(source.with_suffix('.ld')),
                            str(obj), '-o', str(elf)], check=True)
            for section, destinations in sections.items():
                binary = tmp / (stem + section + '.bin')
                subprocess.run(['llvm-objcopy', '--dump-section', section + '=' + str(binary),
                                str(elf)], check=True)
                code = binary.read_bytes()
                require(bool(code), 'Empty helper section')
                for address in destinations:
                    require(all(mapping.get(address + i) == v for i, v in enumerate(code)),
                            f'Assembly differs: {stem}{section} at {address:#x}')
                    compared += len(code)
            print('PASS:', stem)
    print(f'PASS: {compared} helper bytes match the distributed patches; no gameplay test.')


if __name__ == '__main__':
    main()
