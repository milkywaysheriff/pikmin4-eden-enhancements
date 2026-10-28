// Preserve the real delta before the native movement-state update reuses S8.
// The native method has only register arguments (X0/X1/W2/S0). Its own
// 0xF0 frame/offsets stay intact. An outer 16-byte frame holds LR and delta.
.text
.global progress_entry, decay_entry, delta_load
progress_entry:
    stp x30, xzr, [sp, #-16]!
    str s0, [sp, #8]
    bl native_body
    ldr x30, [sp], #16
    ret
native_body:
    sub sp, sp, #0xf0           // displaced native first instruction
    b native_resume

// Native recovery decay -1/60 per update becomes -0.5 * actual seconds.
// Keep the original S1 counter and every other register/flag unchanged.
decay_entry:
    str q2, [sp, #-16]!
    ldr s0, [sp, #0x108]       // native SP+0xF8 plus this temporary frame
    fmov s2, #-0.5
    fmul s0, s0, s2
    ldr q2, [sp], #16
    b decay_resume

.section .delta,"ax"
delta_load:
    ldr s0, [sp, #0xf8]        // feeds expected progress AND stuck increment
