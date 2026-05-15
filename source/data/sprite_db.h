#include "core/enums.h"
#include "core/structs.h"
// grit-generated headers
// moons
#include "moon-0.h"
// days of the week
#include "tuesday.h"
// numbers
#include "number-0.h"
#include "number-1.h"
#include "number-2.h"
#include "number-3.h"
#include "number-4.h"
#include "number-5.h"
#include "number-6.h"
#include "number-7.h"
#include "number-8.h"
#include "number-9.h"
// time text
#include "afternnoon-0-0.h"
#include "afternnoon-1-0.h"
#include "afternnoon-2-0.h"
// skills
#include "skills-level.h"

// sprites sharing a palette should point at the same array
const SpriteDBEntry SPRITE_DB[] = {
    // type, id, tiles, tilesLen,  pal, palLen
    { MOON,         MOON_0,          moon_0Tiles,        moon_0TilesLen,        moon_0Pal,        moon_0PalLen },
    { DAY_OF_WEEK,  TUESDAY,         tuesdayTiles,       tuesdayTilesLen,       tuesdayPal,       tuesdayPalLen },
    { DIGIT,        DIGIT_0,         number_0Tiles,      number_0TilesLen,      number_0Pal,      number_0PalLen },
    { DIGIT,        DIGIT_1,         number_1Tiles,      number_1TilesLen,      number_1Pal,      number_1PalLen },
    { DIGIT,        DIGIT_2,         number_2Tiles,      number_2TilesLen,      number_2Pal,      number_2PalLen },
    { DIGIT,        DIGIT_3,         number_3Tiles,      number_3TilesLen,      number_3Pal,      number_3PalLen },
    { DIGIT,        DIGIT_4,         number_4Tiles,      number_4TilesLen,      number_4Pal,      number_4PalLen },
    { DIGIT,        DIGIT_5,         number_5Tiles,      number_5TilesLen,      number_5Pal,      number_5PalLen },
    { DIGIT,        DIGIT_6,         number_6Tiles,      number_6TilesLen,      number_6Pal,      number_6PalLen },
    { DIGIT,        DIGIT_7,         number_7Tiles,      number_7TilesLen,      number_7Pal,      number_7PalLen },
    { DIGIT,        DIGIT_8,         number_8Tiles,      number_8TilesLen,      number_8Pal,      number_8PalLen },
    { DIGIT,        DIGIT_9,         number_9Tiles,      number_9TilesLen,      number_9Pal,      number_9PalLen },
    { TIME,         AFTERNOON_0_0,   afternnoon_0_0Tiles,afternnoon_0_0TilesLen,afternnoon_0_0Pal,afternnoon_0_0PalLen },
    { TIME,         AFTERNOON_1_0,   afternnoon_1_0Tiles,afternnoon_1_0TilesLen,afternnoon_1_0Pal,afternnoon_1_0PalLen },
    { TIME,         AFTERNOON_2_0,   afternnoon_2_0Tiles,afternnoon_2_0TilesLen,afternnoon_2_0Pal,afternnoon_2_0PalLen },
    { SKILL_SPRITE, SKILLS_LEVEL,    skills_levelTiles,  skills_levelTilesLen,  skills_levelPal,  skills_levelPalLen },
};

const int SPRITE_DB_LEN = sizeof(SPRITE_DB) / sizeof(SPRITE_DB[0]);
