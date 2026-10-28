ENTRY(no_chromatic)
PHDRS { code PT_LOAD; }
SECTIONS {
    .text 0x062F0A40 : { *(.text) } :code
    ASSERT(SIZEOF(.text) == 12, "CA helper changed size")
    ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x062F0AA0, "DR cave conflict")
    /DISCARD/ : { *(.comment) *(.note*) }
}
native_resume = 0x05936ED0;
