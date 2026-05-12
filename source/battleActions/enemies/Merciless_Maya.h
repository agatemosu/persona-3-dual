#pragma once
#include "Enemy.h"
#include "../skills/AttackSkill.h"
#include "../skills/Strike_Attack.h"
#include "../skills/Agi.h"

struct Merciless_Maya : Enemy
{
    Strike_Attack strike_Attack;
    Agi agi;
    AttackSkill *myAttackSkill[1];

    Merciless_Maya()
    {
        baseAttackAction = &strike_Attack;
        myAttackSkill[0] = &agi;

        name = "Merciless Maya";
        hp = 83;
        sp = 15;
        lv = 2;
        st = 2;
        ma = 4;
        en = 3;
        ag = 2;
        lu = 2;
        attackSkill = myAttackSkill;
        attackCount = 1;

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
