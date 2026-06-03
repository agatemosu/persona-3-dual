#pragma once
#include <nds.h>
#include <stdio.h>

inline bool DeductAttackCost(s32* stat, s32 cost, const char* insufficientMessage)
{
    if (*stat < cost)
    {
        iprintf(insufficientMessage);
        return false;
    }
    *stat -= cost;
    return true;
}
