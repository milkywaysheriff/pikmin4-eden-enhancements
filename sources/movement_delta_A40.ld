ENTRY(enter_call)
PHDRS { delta2 PT_LOAD; delta1 PT_LOAD; progress PT_LOAD; ride PT_LOAD; }
SECTIONS {
    .delta2 0x01A399E4 : { *(.delta2) } :delta2
    .delta1 0x01A39A18 : { *(.delta1) } :delta1
    .progress 0x062F0BB4 : { *(.progress) } :progress
    ASSERT(SIZEOF(.progress) == 24, "Progress helpers changed size")
    ASSERT(ADDR(.progress) + SIZEOF(.progress) <= 0x062F0C00, "Viewport conflict")
    .ride 0x062F0E20 : { *(.ride) } :ride
    ASSERT(SIZEOF(.ride) <= 0x1E0, "Ride helpers exceed free padding")
    /DISCARD/ : { *(.comment) *(.note*) }
}
fallback_call_resume = 0x01A3B660;
fallback_resume = 0x01A39924;
app_delta = 0x08DA9418;
step30 = 0x07F1BCF0;
native_ride_helper = 0x016B4EA0;
reciprocal_resume = 0x016B4F5C;
gravity_resume = 0x016B4FB8;
