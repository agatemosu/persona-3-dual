#pragma once
#include "AttackSkill.h"

struct Garu : AttackSkill
{
    Garu()
    {
        movePower = 40;
        race = mag;
        element = Wind;
        cost = 3;
        name = "Garu";
        hitRate = 99;
        skillTarget = SkillTarget::OppositionTeam;
    }
};
