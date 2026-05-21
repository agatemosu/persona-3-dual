#pragma once
#include "AttackSkill.h"

struct Agi : AttackSkill
{
    Agi()
    {
        movePower = 40;
        race = mag;
        element = Fire;
        cost = 3;
        name = "Agi";
        hitRate = 99;
        skillTarget = SkillTarget::OppositionTeam;
    }
};
