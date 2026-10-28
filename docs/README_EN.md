# Installation and options

For **Pikmin 4 update 1.1.1 on Eden**.
This is a modular beta: install only the options you want.

| Archive group | Options | Selection |
|---|---|---|
| `01_FPS_choose_one` | 60, 120 or 180 FPS target | At most one |
| `02_Timing` | Pikmin Movement and Timers: fixes following and jumping onto Oatchi at higher FPS | Required with any included FPS mod |
| `03_Camera_choose_one` | Manual camera rotation +12.5%, +25%, +50%, +75% or +100% | At most one |
| `04_Ultrawide_choose_one` | 3440×1440 or 5120×2160 | At most one |
| `05_Optional` | Chromatic Aberration OFF; Dynamic Resolution Lock | Either or both |

Camera and graphics options can be used without changing the frame rate.
To return to the original 30 FPS timing, disable all FPS mods and the
Pikmin Movement and Timers mod.

## Install

1. Download the main mod ZIP from the release and extract it outside
   Eden's mod directory. The Sources ZIP is for development.
2. Stop emulation and close Eden. Back up existing mods for the same
   features outside the mod directory.
3. Find Pikmin 4's mod data location from the game's right-click menu in
   Eden. Close Eden again before copying files.
4. Copy **only your chosen `P4 - ...` folders** from inside the numbered
   groups directly into that location. Do not copy the archive root or
   the numbered group folders there.
5. Reopen Eden and enable your choices in the game's properties, with
   update **1.1.1** selected. Keep emulation speed at **100%**.

An FPS option must be installed like this:

```text
<Pikmin 4 mod directory>/
  P4 - FPS 60/
    exefs/1.1.1.pchtxt
    exefs/1.1.1_sdk.pchtxt
  P4 - Pikmin Movement and Timers/
    exefs/1.1.1.pchtxt
```

Keep **both main and SDK files** of your FPS option and enable the
separate movement/timing mod too. Never enable several FPS, camera or
ultrawide variants together. When upgrading, remove older equivalent
folders first: installing a newly named copy does not disable the old one.

## Options and settings

**FPS:** targets 60, 120 or 180 FPS. Achieved FPS depends on performance.
120 FPS is experimental; 180 FPS has not been play-tested locally.

**Pikmin Movement and Timers:** adjusts following, movement progress
checks and jumping onto Oatchi for higher frame rates. It does not fix
every frame-dependent system in the game.

**Camera:** increases manual rotation speed, not camera distance or zoom.

**Ultrawide:** adapts perspective for each player view. Use **GPU High**,
Eden scale **1×**, **Stretch to Window** and a matching image area. The
5120×2160 version has positive feedback, including the two player views
shown during Dandori battles. The current 3440×1440 variant has not yet
been play-tested. No 32:9 option is supplied. Exact aspect ratios are
64:27 and 43:18 respectively, both commonly called 21:9.

Do not apply another 4× scale or stack another output/projection mod.
GPU Low caused a yellow rendering glitch in earlier local tests,
particularly after returning to the title and loading again. The local
setup uses CPU Unsafe; these mods do not change CPU settings.

**Chromatic Aberration OFF:** sets the final colored-fringe intensity to
zero. A controlled visual comparison has not been recorded.

**Dynamic Resolution Lock:** keeps the game's minimum resolution equal
to its profile maximum. It does not force 100% screen percentage or prove
the internal 3D render size. Ultrawide dimensions are requested viewports.

## Removal and support

Close Eden and remove the folders installed from this pack. Restore your
backup for your previous setup. The download does not replace game files,
saves or emulator configuration.

Other game updates, emulators, platforms and unrelated mods are unverified.
When reporting a problem, include selected options, Eden build, actual FPS
and a reproducible scene. Evidence and limits are in `VERIFICATION.md`.
