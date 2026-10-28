// Replace only the completed perspective projection hook in UW2160.
// The original ViewRect is per-view, including each split-screen player.
// Keep the current vertical projection (M11), FOV policy and UI hooks.
.text
.global projection_per_view
projection_per_view:
    str w8, [x19, #0x8c]         // displaced native store
    stp x8, x9, [sp, #-16]!
    stp x10, x11, [sp, #-16]!
    stp q30, q31, [sp, #-32]!

    ldp x8, x9, [x19, #0x90]
    stp x8, x9, [x19, #0xa0]     // retain this player's whole ViewRect
    ldrb w8, [x20, #0x31]
    cbnz w8, restore              // preserve the existing orthographic path

    ldp w8, w9, [x19, #0x90]     // MinX, MinY
    ldp w10, w11, [x19, #0x98]   // MaxX, MaxY
    sub w8, w10, w8
    sub w9, w11, w9
    // A zero/reversed rectangle can occur during layout transitions.
    // Avoid divisions in that case. These checks do not change NZCV.
    cbz w8, restore
    cbz w9, restore
    tbnz w8, #31, restore
    tbnz w9, #31, restore

    scvtf s30, w8
    scvtf s31, w9
    fdiv s30, s30, s31           // aspect of THIS view, not the full display
    ldr s31, [x19, #0x64]        // unchanged current M11
    fdiv s31, s31, s30
    str s31, [x19, #0x50]        // M00=M11/(ViewWidth/ViewHeight)
restore:
    ldp q30, q31, [sp], #32
    ldp x10, x11, [sp], #16
    ldp x8, x9, [sp], #16
    b native_resume
