#pragma once
#include "Enemy.h"
#include "../skills/AttackSkill.h"
#include "../skills/Slash_Attack.h"
#include "../skills/Agi.h"

struct Merciless_Maya : Enemy
{
    Slash_Attack slash_Attack;
    Agi agi;
    AttackSkill *myAttackSkill[2];

    Merciless_Maya()
    {
        myAttackSkill[0] = &slash_Attack;
        myAttackSkill[1] = &agi;

        name = "Merciless Maya";
        hp = 70;
        sp = 3;
        lv = 3;
        st = 4;
        ma = 4;
        en = 3;
        ag = 3;
        lu = 2;
        attackSkill = myAttackSkill;
        attackCount = 2;

        affinities[Element::Slash] = Weak;
        affinities[Element::Strike] = Neutral;
        affinities[Element::Pierce] = Neutral;
        affinities[Element::Fire] = Resist;
        affinities[Element::Ice] = Weak;
        affinities[Element::Electricity] = Null;
        affinities[Element::Wind] = Neutral;
        affinities[Element::Light] = Neutral;
        affinities[Element::Dark] = Neutral;
    }
};
