#include "AttackSkill.h"

const float AttackSkill::levelMultipliers[24] = {
    0.5f, 0.51f, 0.53f, 0.59f, 0.66f,
    0.75f, 0.84f, 0.91f, 0.97f, 0.99f,
    1.0f, 1.0f, 1.0f, 1.0f,
    1.01f, 1.03f, 1.09f, 1.16f, 1.25f,
    1.34f, 1.41f, 1.47f, 1.49f, 1.5f};

void AttackSkill::damageSetup(BattleStats *attackerStats, BattleStats *defenderStats, u32 *attackerLevel, u32 *defenderLevel)
{
    if (race == phys)
        Atk = attackerStats->st;
    else
        Atk = attackerStats->ma;

    diff = *attackerLevel - *defenderLevel;
    if (diff < -13)
        diff = -13;
    else if (diff > 10)
        diff = 10;

    levelDifference = levelMultipliers[diff + 13]; // offset so -13 is 0

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
}
