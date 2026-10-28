// End of native view postprocess overrides, including SceneColorFringe.Max.
// Clear only the final fringe intensity, then replay the native load.
// No changes to shader registration, exposure, tone mapping or other effects.
.text
.global no_chromatic
no_chromatic:
    str wzr, [x19, #0x10a4]
    ldr x10, [x19]
    b native_resume
