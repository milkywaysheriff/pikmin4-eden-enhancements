# Test coverage and limitations

The options in this beta have different levels of testing. A patch loading
successfully does not establish that every game mode works or that the
selected frame rate target was reached.

| Component | Evidence | Remaining limits |
|---|---|---|
| 60 FPS | Loaded in the latest local play session | No complete campaign benchmark |
| 120 FPS with movement fixes | Positive feedback for following and boarding Oatchi in earlier tests | FPS during those successful tests was not captured; not every timing path is confirmed |
| 180 FPS | Code/package checks | No local gameplay test |
| Movement and timers | Earlier following/boarding fixes have positive feedback; later additions load successfully | Additional timer paths not separately confirmed; not a fix for every frame-dependent system |
| Camera +50% | Current local option, loaded successfully | Other speeds lack individual confirmation in the current setup |
| Ultrawide 5120×2160 | Positive feedback for single-player UI/proportions and corrected 3D in the two player views of Dandori battles | Latest recorded session uses 60 FPS; full mode/FPS coverage not established |
| Ultrawide 3440×1440 | Same projection method with a different viewport request; geometry checks | No gameplay test of this exact version |
| Chromatic Aberration OFF | Final intensity field patched to zero; patch loads | Controlled visual comparison not recorded |
| Dynamic Resolution Lock | Current local option, loaded successfully | Actual internal 3D render size/density not measured |

The 5120×2160 split-view correction was reported by gallongg on 28 October 2026.
The latest log is from Eden nightly a594c8d60e. Earlier stages also used
stable v0.2.1; this is not validation of every build/platform.

Earlier GPU High tests reported no yellow rendering glitch, including a
return to the title followed by reloading the save. GPU High remains part
of the recommended ultrawide setup. That feedback is not a new visual
comparison of every graphics option.

Offline checks validate input hashes, Build IDs, patch bytes, archive
extraction and 288 permitted feature combinations for overlapping writes.
The newer helper assembly is reassembled and compared to the patches.
Limited instruction/geometry models do not execute the game or GPU.
Compatibility with unrelated mods is unverified.
