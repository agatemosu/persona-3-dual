#pragma once
#include <nds.h>
#include "Element.h"

struct BattleStats
{
    u32 st;
    u32 ma;
    u32 en;
    u32 ag;
    u32 lu;

    enum Affinity
    {
        Neutral,
        Weak,
        Resist,
        Null,
        Absorb,
        Repel
    };

    // this works for now but if you have a better idea leave a message (idk map?)

    Affinity affinities[10] = {
        Neutral,
        Neutral,
        Neutral,
        Neutral,
        Neutral,
        Neutral,
        Neutral,
        Neutral,
        Neutral,
        Neutral // almighty
    };

    BattleStats *getBattleStats()
    {
        return this;
    };
    // add afinites
};
