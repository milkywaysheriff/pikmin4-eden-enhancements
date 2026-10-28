ENTRY(follow_entry)
PHDRS { timers PT_LOAD; delta PT_LOAD; }
SECTIONS {
    .follow_delta 0 : { *(.follow_delta) } :delta
    .timers 0x062F0EA8 : { *(.timers) } :timers
    ASSERT(SIZEOF(.timers) == 160, "Timer helpers changed size")
    ASSERT(ADDR(.timers) + SIZEOF(.timers) <= 0x062F1000, "Executable padding exceeded")
    /DISCARD/ : { *(.comment) *(.note*) }
}
follow_resume = 0x0135AB94;
app_delta = 0x08DA9418;
contact_first_resume = 0x013529E8;
contact_second_resume = 0x01352E7C;
velocity_resume = 0x013705E8;
