#pragma once
#include <nds.h>
#include "skills/AttackSkill.h"

inline auto DeductAttackCost = [](s32 *stat, s32 cost, const char *msg) -> bool
{
    if (*stat < cost)
    {
        iprintf(msg);
        return false;
    }
    *stat -= cost;
    return true;
};
