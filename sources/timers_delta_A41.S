// Cumulative extension of A40, not a replacement for its movement fixes.
// Follow Update has register arguments X0/X1/W2/S0. Protect its incoming
// delta in an outer frame: native S8 is reused later in this large method.
.section .timers,"ax"
.global follow_entry, contact_first, contact_second, actor_velocity
follow_entry:
    stp x30, xzr, [sp, #-16]!
    str s0, [sp, #8]
    bl follow_body
    ldr x30, [sp], #16
    ret
follow_body:
    sub sp, sp, #0x1e0
    b follow_resume

// The shared contact helper has no delta argument. Use the FApp step
// matched to AI/movement by A35 in normal gameplay. X8 and NZCV survive;
// S1 is exactly the destination of the displaced native LDR S1.
contact_first:
    str x8, [sp, #-16]!
    adrp x8, app_delta
    ldr d1, [x8, #:lo12:app_delta]
    fcvt s1, d1
    ldr x8, [sp], #16
    b contact_first_resume
contact_second:
    str x8, [sp, #-16]!
    adrp x8, app_delta
    ldr d1, [x8, #:lo12:app_delta]
    fcvt s1, d1
    ldr x8, [sp], #16
    b contact_second_resume

// Another Follow transition estimates the target speed from the exact same
// Actor current/previous position cache used by A40 RideOn. At 30Hz the
// factor is bit-identical to its native 30.0 (30/(30*float(dt))).
actor_velocity:
    stp x8, x9, [sp, #-32]!
    str q4, [sp, #16]
    mrs x9, nzcv
    adrp x8, app_delta
    ldr d3, [x8, #:lo12:app_delta]
    fcvt s3, d3
    fcmp s3, #0.0
    b.le velocity_default
    fmov w8, s3
    ubfx w8, w8, #23, #8
    cmp w8, #255
    b.eq velocity_default
    fmov s4, #30.0
    fmul s3, s3, s4
    fdiv s3, s4, s3
    b velocity_done
velocity_default:
    fmov s3, #30.0
velocity_done:
    msr nzcv, x9
    ldr q4, [sp, #16]
    ldp x8, x9, [sp], #32
    b velocity_resume

.section .follow_delta,"ax"
    ldr s1, [sp, #0x1e8]
