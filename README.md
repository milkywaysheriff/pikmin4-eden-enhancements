# Pikmin 4 — Eden Enhancements

Optional mods for **Pikmin 4 1.1.1 on Eden**: higher frame rates, faster camera controls, ultrawide support and graphics adjustments. Choose the features you want and leave the rest off.

**[Download the beta](https://github.com/milkywaysheriff/pikmin4-eden-enhancements/releases/tag/v1.0.0-beta.1)**
· [Installation](docs/README_EN.md) · [Italiano](docs/LEGGIMI_IT.md)

## Features

| Mod | What it does | Options |
|---|---|---|
| Higher frame rate | Raises the frame rate target for smoother gameplay | 60, 120 or 180 FPS |
| Pikmin movement fixes | Corrects frame rate dependent behavior when Pikmin follow you or jump onto Oatchi | Use with any included FPS mod |
| Faster camera | Increases how quickly the camera turns when you move the camera stick | +12.5%, +25%, +50%, +75% or +100% |
| Ultrawide | Adapts the game view for wide screens while keeping natural proportions | 3440×1440 or 5120×2160 |
| Chromatic Aberration OFF | Disables the colored fringe effect around image edges | Optional |
| Dynamic Resolution Lock | Keeps dynamic resolution at the maximum chosen by the game's current profile | Optional |

## Quick installation

1. Download the **mod ZIP attached to the release** and extract it outside Eden's mod folder.
2. Close Eden and back up older mods that change the same features.
3. Copy only your selected `P4 - ...` folders from inside the numbered groups into Pikmin 4's mod data location. Find this location by right-clicking the game in Eden.
4. Enable your choices in the game's properties, with update **1.1.1** active.
5. Set GPU Accuracy in Eden to "Accurate" or graphical glitches will appear. Sometimes they still appear even with this setting, you just need to restart the game.

Choose **one FPS option**, **one camera speed** and **one ultrawide resolution** at most. Every FPS option needs both files in its `exefs` folder and the separate **Pikmin Movement and Timers** mod.

For ultrawide, use Eden **1×**, GPU accuracy **High**, **Stretch to Window** and an image area matching the chosen resolution. Keep emulation speed at **100%**. Close Eden and remove the installed folders to uninstall; restore your backup for your previous mod setup.

## Beta status

The local play setup uses 60 FPS and 5120×2160. Movement improvements have positive gameplay feedback. The 120 FPS option is experimental; **180 FPS and the current 3440×1440 variant have not been play-tested locally**. Other options have different levels of verification.

FPS options set targets; hardware and the scene determine actual FPS. Viewport sizes do not establish internal 3D render resolution. Dynamic Resolution Lock does not force 100% screen percentage. See [test coverage](docs/VERIFICATION.md) for details. Other updates, emulators, platforms and unrelated mods are unverified.

## Source and development

The separate **Sources ZIP** contains patch templates and helper assembly. Python 3.9+ standard library is enough to build the downloads:

```sh
python3 tools/build_release.py
python3 -m unittest discover -s tests -v
```

With LLVM installed, check the supplied assembly with:

```sh
python3 tools/verify_sources.py
```

These are offline code/packaging checks, not game tests.
See [source notes](docs/SOURCE_NOTES.md).

Maintained by [milkywaysheriff](https://github.com/milkywaysheriff).
Development used OpenAI Codex assistance; earlier reference work is credited
to Fl4sh9174. Full acknowledgements are in [Credits](docs/CREDITS.md).
