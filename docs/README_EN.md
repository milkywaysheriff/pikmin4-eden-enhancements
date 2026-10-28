# Pikmin 4 — Eden Enhancements 1.0-beta1

Published by **gallongg**. For **Pikmin 4 update 1.1.1**, title ID
`0100B7C00933A000`, on Eden. This is a modular beta, with different levels
of gameplay verification for each option. Read `VERIFICATION.md`.

## Choose your options

| Package group | Options | Selection rule |
|---|---|---|
| `01_FPS_choose_one` | 60, 120, 180 FPS | At most one; 120/180 are experimental |
| `02_Timing` | Pikmin Movement and Timers A41 | Required with any included FPS option |
| `03_Camera_choose_one` | +12.5%, +25%, +50%, +75%, +100% | At most one; changes manual rotation speed, not camera distance |
| `04_Ultrawide_choose_one` | 5120×2160 or 3440×1440, A45 | At most one; both use the per-view projection method |
| `05_Optional` | Chromatic Aberration OFF; Dynamic Resolution Lock | Independently optional |

You can use camera or optional graphics patches without changing the FPS.
Disable all FPS options to return to the game's original 30 FPS behavior;
also disable this pack's timing patch for an unmodified timing baseline.

The most recently recorded local setup used **60 FPS + timing A41 + camera
+50% + ultrawide 5120×2160 A45 + CA OFF + DR Lock**. This is a record of the
tested configuration, not a claim that all options have equal coverage.

## Installation

1. Stop emulation and close Eden. Back up your existing Pikmin 4 mod folders
   somewhere outside the mod directory.
2. In Eden, right-click Pikmin 4 and open its mod data location, then close
   Eden again before copying files. Use this action to find your actual
   profile; no Linux-specific install path is assumed.
3. Choose the options you want. Copy **only the selected `P4 - ...` folders**
   from inside the numbered groups directly into the game's mod directory.
   Do not copy the archive root or the numbered grouping folders there.
4. Each installed mod must have this structure:

   ```text
   <Pikmin 4 mod directory>/
     P4 - FPS 60 - v4/
       exefs/1.1.1.pchtxt
       exefs/1.1.1_sdk.pchtxt
     P4 - Pikmin Movement and Timers - A41/
       exefs/1.1.1.pchtxt
   ```

5. If you select an FPS option, copy **both files** in its `exefs` folder
   and install/enable A41 from `02_Timing` as well.
6. Open Eden, enable your chosen options in the game's properties and
   confirm update **1.1.1** is selected. Keep emulation speed at **100%**.
   Do not combine several FPS, camera, or ultrawide variants.

If upgrading from the author's earlier local/test packages, move the old
equivalent folders out first: `FPS ... v4`, `Camera ... v3`,
`TEST - Follow progress delta ... A38` (which may already contain A41),
`TEST - Ultrawide ... v6` (which may already contain A45), and old CA/DR
copies. The new folder names do not disable the old copies automatically.

## Ultrawide settings

Use **GPU accuracy High**, Eden resolution scale **1×**, and **Stretch to
Window** with a window/display area matching the chosen dimensions. The
local setup used CPU Unsafe; this pack does not change CPU settings.
The tested High setting matters: a yellow rendering glitch previously
appeared with GPU Low, particularly after returning to the title and
loading a save again. Do not multiply these viewports by another 4× scale.

Both resolutions are commonly called 21:9, but their exact ratios differ:
5120×2160 is 64:27 and 3440×1440 is 43:18. Avoid stretching either to a
32:9 screen. No 32:9 variant is supplied in this release.

A45 derives the perspective aspect from each individual view rectangle,
including split screen. Corrected Dandori 3D proportions have been reported
for the 5120×2160 version. The 3440×1440 A45 version changes only the viewport
string and has not yet been tested in gameplay.

These are **requested game viewport sizes**. Internal 3D render resolution
has not been measured. DR Lock keeps the game's minimum equal to its own
profile maximum; it does not force 100% screen percentage or guarantee
1:1 rendering. Higher FPS targets also require sufficient performance;
the 120 FPS patch does not guarantee that every scene reaches 120 FPS.

## Compatibility and removal

This release supplies ExeFS `pchtxt` patches for Eden. Other game updates,
emulators, Switch hardware, online modes and frame generation have not
been validated. It contains no IPS conversion or console install files.
Avoid other FPS/clock, timing, projection/output, camera speed, CA or DR
patches that modify the same features. Compatibility with unrelated mods
is not implied by the internal byte-overlap checks.

To change a variant, close Eden, move the previous `P4 - ...` variant out,
then install only its replacement. To uninstall, close Eden and move this
pack's folders out of the mod directory. Restore your backed-up folders
to recover your exact previous mod setup; keep the settings you recorded
before installation. No game, save, firmware or INI file is replaced.

`CREDITS.md` identifies project contributions and earlier references.
Stop Talking is a separate third-party mod and is not bundled.
