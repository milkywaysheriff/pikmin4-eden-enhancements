// Extend A38 without overwriting its hooks/helper.
// The legacy progress helper's 0x60 frame has an unused 8-byte slot at+8.
.section .progress,"ax"
.global fallback_call, fallback_entry
fallback_call:
    ldr s0, [sp, #0xf8]      // entry delta held by the existing A38 wrapper
    mov x0, x21             // displaced native argument setup
    b fallback_call_resume  // original BL to the legacy progress helper
fallback_entry:
    str d14, [sp, #-0x60]!   // displaced native prologue, same frame size
    str s0, [sp, #8]         // private unused padding within this frame
    b fallback_resume

.section .ride,"ax"
.global enter_call, update_call, reciprocal, gravity
// RideOn has two direct callers. Protect Q4, LR/X9 and incoming NZCV.
// Enter has no dt argument: initial target-motion compensation uses the
// current FApp step (matched to AI/move dt by the A35 normal-gameplay trace).
enter_call:
    stp x30, x9, [sp, #-48]!
    str q4, [sp, #16]
    adrp x9, app_delta
    ldr d4, [x9, #:lo12:app_delta]
    fcvt s4, d4
    b checked_call
update_call:
    stp x30, x9, [sp, #-48]!
    str q4, [sp, #16]
    fmov s4, s8             // native RideOn Update's real incoming delta
checked_call:
    mrs x9, nzcv
    str x9, [sp, #32]
    fcmp s4, #0.0
    b.le default_step        // also covers unordered/NaN
    fmov w9, s4
    ubfx w9, w9, #23, #8
    cmp w9, #255
    b.ne step_ready
default_step:
    adrp x9, step30
    ldr s4, [x9, #:lo12:step30]
step_ready:
    ldr x9, [sp, #32]
    msr nzcv, x9
    bl native_ride_helper
    ldr q4, [sp, #16]
    ldp x30, x9, [sp], #48
    ret

// At30, 1/float(1/30) is exactly the native 29.999998092651367.
// S1 is overwritten by the native DUP immediately after this hook.
reciprocal:
    fmov s1, #1.0
    fdiv s1, s1, s4
    fmov w11, s1
    b reciprocal_resume

// Preserve the native acceleration value; scale its per30Hz-step decrement
// by30*dt instead of applying a full original step on every120Hz update.
// Q4 is private scratch until restored by the two call wrappers above.
gravity:
    fmov s3, #30.0
    fmul s3, s4, s3
    ldr s4, [x11, #0x3a8]
    fmul s3, s4, s3
    b gravity_resume

.section .delta2,"ax"
    ldr s2, [sp, #8]
.section .delta1,"ax"
    ldr s1, [sp, #8]
