#pragma once
#include "AttackSkill.h"

struct Dia : AttackSkill
{
    Dia()
    {
        movePower = 50;
        race = mag;
        element = Heal;
        cost = 3;
        name = "Dia";
        hitRate = 100;
        skillTarget = SkillTarget::OwnTeam;
    }
};
