#pragma once
#include <nds.h>
#include <cmath>
#include <stdlib.h>
#include <stdio.h>
#include <string>
#include "../Element.h"
#include "../BattleStats.h"

struct AttackSkill
{
    float moveDamage;
    enum Race
    {
        phys,
        mag
    };

    u32 cost;
    Race race;
    u32 element;
    std::string name;

    u32 calculateDamage(BattleStats *attackerStats, BattleStats *defenderStats, u32 *attackerLevel, u32 *defenderLevel)
    {
        u32 Atk;
        if (race == phys)
            Atk = attackerStats->st;
        else
            Atk = attackerStats->ma;

        s32 diff = *attackerLevel - *defenderLevel;
        if (diff < -13)
            diff = -13;
        else if (diff > 10)
            diff = 10;

        float levelDifference = levelMultipliers[diff + 13]; // offset so -13 is 0

        float affinityMtp = 1.0f;
        u32 affinity = defenderStats->affinities[element];

        if (affinity == BattleStats::Affinity::Weak)
            affinityMtp = 1.25f;
        else if (affinity == BattleStats::Affinity::Neutral)
            affinityMtp = 1.0f;
        else if (affinity == BattleStats::Affinity::Resist)
            affinityMtp = 0.5f;
        else if (affinity == BattleStats::Affinity::Null)
            affinityMtp = 0.0f;
        else if (affinity == BattleStats::Affinity::Absorb)
            affinityMtp = -1.0f;
        // TODO: add repel logic
        else if (affinity == BattleStats::Affinity::Repel)
            affinityMtp = -2.0f;

        // todo: level diffrence never goes under 0 for either party during boss fights
        u32 result = (u32)floor(sqrt((float)(moveDamage * 15 * Atk) / defenderStats->en) * 2 * levelDifference * affinityMtp);
        return result;
    }

    virtual ~AttackSkill() = default;

private:
    static const float levelMultipliers[24];
};
