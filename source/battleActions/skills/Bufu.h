#pragma once
#include "AttackSkill.h"

struct Bufu : AttackSkill
{
    Bufu()
    {
        movePower = 40;
        race = mag;
        element = Ice;
        cost = 3;
        name = "Bufu";
        hitRate = 99;
        skillTarget = SkillTarget::OppositionTeam;
    }
};
