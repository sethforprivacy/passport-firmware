// Passport wallet font definitions in C
// Autogenerated by bdf-to-passport.py: DO NOT EDIT
#pragma once

#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>

typedef struct {
    int8_t x;
    int8_t y;
    int8_t w;
    int8_t h;
    int8_t advance;
    uint8_t* bitmap;
} GlyphInfo;

typedef struct {
    int8_t x;
    int8_t y;
    int8_t w;
    int8_t h;
    int8_t advance;
    uint8_t data_len;
} BBox;

typedef struct {
    uint16_t range_start;
    uint16_t range_end;
    uint16_t* bitmap_offsets;
} Codepoints;

typedef struct {
    int8_t height;
    int8_t advance;
    int8_t ascent;
    int8_t descent;
    int8_t leading;
    uint8_t codepoint_start;
    uint8_t codepoint_end;
    uint8_t num_codepoint_ranges;
    BBox* bboxes;
    Codepoints* codepoints;
    uint8_t* bitmaps;
} Font;

// Lookup GlyphInfo for a single codepoint or return None
bool glyph_lookup(Font* font, uint8_t cp, GlyphInfo* glyph_info);

// Font references
extern Font FontTiny;
extern Font FontSmall;