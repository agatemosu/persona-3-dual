#pragma once
#include <nds.h>
#include "skills/AttackSkill.h"

inline auto DeductAttackCost = [](u32 *stat, u32 cost, const char *msg) -> bool
{
    if (*stat < cost)
    {
        iprintf(msg);
        return false;
    }
    *stat -= cost;
    return true;
};
