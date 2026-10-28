ENTRY(progress_entry)
PHDRS { delta PT_LOAD; helper PT_LOAD; }
SECTIONS {
    .delta 0x01A3B148 : { *(.delta) } :delta
    ASSERT(SIZEOF(.delta) == 4, "Delta replacement must be one instruction")
    .text 0x062F0B80 : { *(.text) } :helper
    ASSERT(SIZEOF(.text) <= 0x80, "Helper overlaps viewport hook")
    /DISCARD/ : { *(.comment) *(.note*) }
}
native_resume = 0x01A3ADB4;
decay_resume = 0x01A3B170;
