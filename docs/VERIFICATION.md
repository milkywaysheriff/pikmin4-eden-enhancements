# Verification and beta limits — 28 October 2026

User observations and offline checks have different scopes. A patch
appearing in an Eden log proves it was applied, not that every feature
worked correctly or reached the advertised FPS target.

| Component | Recorded evidence | Limits |
|---|---|---|
| FPS60 v4 | Applied in the latest logged play session | No complete campaign benchmark |
| FPS120 v4 + movement correction | User reported corrected following and Oatchi boarding for A38/A40 | FPS during those successful tests was not captured; A41 additions not individually confirmed |
| FPS180 v4 | Included project variant, byte compatibility checked | Gameplay `not_run`; experimental |
| Timing A41 | Cumulative A38/A40 bytes retained; applied in the latest log | Six added timers and a velocity estimate lack separate gameplay confirmation; remaining game timing systems still open |
| Camera +50% v3 | Current option applied in the latest log | Other supplied speeds not individually verified in the current setup |
| UW5120×2160 A45 | User explicitly reports Dandori split-screen views fixed after latest update; installed SHA and latest application log confirmed | Latest recorded run uses FPS60. This does not establish split correctness at every FPS/mode |
| UW3440×1440 A45 | Same per-view code, only viewport string changed; offline full/half-view geometry checked | Exact new variant gameplay `not_run`; does not inherit a gameplay pass from the 5120 variant |
| CA OFF A42 | Applied in the latest log; final intensity field patched to zero | Controlled visual comparison not recorded |
| DR Lock v5 | Applied in the latest log | Actual 3D render size and density not measured |

Earlier user tests reported correct single-player UI proportions and no
yellow glitch with GPU High, including returning to the title and loading
again. These observations predate A45. A45's full-view output was checked
offline against the previous 5120 helper; a separate new campaign test has
not been explicitly reported. Dandori confirmation refers to the **3D
proportions** the user had identified as wrong; it is not a new HUD audit.

Packaging checks validate input hashes, Build IDs, syntax, exact patch-byte
equivalence, the sole viewport-string difference, and **288 permitted
feature selections** for overlapping write addresses. This is byte-level
compatibility within this pack, not runtime compatibility with every mod.
The ARM helper checks use limited interpreters/models, not full game/GPU
execution. See the Sources download for the patch sources and packaging tool.

The setup has been used on native Linux Eden, including stable v0.2.1 and
nightly a594c8d60e at different stages. The latest A45 feedback corresponds
to the nightly log. Other builds/platforms are unverified. No guaranteed
FPS, complete timing fix, GPU benchmark or native-resolution claim is made.
