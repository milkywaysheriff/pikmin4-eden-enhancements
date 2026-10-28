ENTRY(projection_per_view)
PHDRS { code PT_LOAD; }
SECTIONS {
    .text 0x062F0C00 : { *(.text) } :code
    ASSERT(SIZEOF(.text) == 104, "Unexpected projection helper size")
    ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x062F0D00, "Resolution parser cave conflict")
    /DISCARD/ : { *(.comment) *(.note*) }
}
native_resume = 0x05226AF4;
