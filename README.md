# Pikmin 4 — Eden Enhancements

Modular **Pikmin 4 1.1.1** patches for Eden, maintained by
**gallongg** ([milkywaysheriff](https://github.com/milkywaysheriff)).

**[Download 1.0 beta 1](https://github.com/milkywaysheriff/pikmin4-eden-enhancements/releases/tag/v1.0.0-beta.1)**
· [Installation](docs/README_EN.md) · [Italiano](docs/LEGGIMI_IT.md)
· [Verification](docs/VERIFICATION.md) · [Credits](docs/CREDITS.md)

This is a **prerelease**. The 5120×2160 Dandori split-screen fix has positive
gameplay feedback. Other options have different test coverage; see the
verification notes before choosing experimental variants.

| Feature | Options |
|---|---|
| FPS target | 60 / 120 / 180; choose one, 120/180 experimental |
| Pikmin movement and timing | Cumulative A41 including following and Oatchi boarding fixes |
| Manual camera rotation speed | +12.5% / +25% / +50% / +75% / +100%; choose one |
| Ultrawide per-view projection | 5120×2160 / 3440×1440; choose one |
| Optional graphics | Chromatic Aberration OFF; Dynamic Resolution Lock |

## Install

Download the **mod ZIP attached to the release**, extract it outside Eden,
and copy only the selected `P4 - ...` folders from inside the numbered
groups to Pikmin 4's mod data location. Close Eden before copying and move
older equivalent mods out first. Enable your choices in the game properties.

Each FPS option needs **both main and SDK patch files**, plus the separate
**A41 timing mod**. Enable at most one FPS, one camera and one ultrawide
variant. Keep emulation speed at 100%.

For ultrawide use **Eden 1×**, **GPU High**, Stretch to Window and a matching
21:9 image area. The local setup uses CPU Unsafe; the patches do not edit
emulator settings. The supplied viewport sizes are requests, not measured
internal 3D render resolutions. FPS targets depend on available performance.

To uninstall, close Eden and remove this pack's mod folders. Restore your
backed-up folders for your previous configuration. Game files, saves and
emulator configuration are not replaced by these downloads.

## Compatibility and evidence

- Only Pikmin 4 **1.1.1**, title ID `0100B7C00933A000`.
- Main build prefix `060F827BD2B38703E9EA11E3210D89BC`; SDK has its own
  full Build ID in the patch/catalog. Do not change IDs to force a patch.
- Dandori 3D proportions corrected with 5120×2160 A45, reported by the
  local tester. The latest recorded session uses FPS60.
- The 3440×1440 A45 variant and FPS180 lack a local gameplay test. A41's
  added timer paths and CA OFF lack separate controlled gameplay/visual
  confirmation. No complete campaign or every-system timing guarantee.
- Byte-level checks cover 288 valid feature selections. They do not prove
  compatibility with unrelated mods or every emulator/build.

## Build and review

Python 3.9+ standard library is enough to reproduce the downloads:

```sh
python3 tools/build_release.py
python3 -m unittest discover -s tests -v
```

Outputs are written to `dist/`. To reassemble the five newer ARM64 helpers
and compare them to the patch bytes, also install LLVM tools and run:

```sh
python3 tools/verify_sources.py
```

No game dump is needed for these packaging/helper checks. See
[source notes](docs/SOURCE_NOTES.md) for the scope: older `pchtxt` templates
are the authoritative source for their patch bytes. Tests do not run the
game or GPU.

## Contributions and provenance

Report the selected options, Eden build, actual FPS and a reproducible scene
when filing a bug. Do not attach game executables, keys, firmware or saves.

gallongg directed and tested the project. Development and documentation
used OpenAI Codex assistance. Earlier 1.0.2 ultrawide/effects references are
credited to Fl4sh9174. Original ZIP/PAK files and the separate **Stop Talking**
mod are not included. This project is unofficial; see
[credits and provenance](docs/CREDITS.md).
