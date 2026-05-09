#pragma once
#include "PersonaBase.h"

#include "../skills/AttackSkill.h"
#include "../skills/Agi.h"
#include "../skills/Bash.h"

struct Orpheus : PersonaBase
{
    Agi agi;
    Bash bash;
    AttackSkill *myAttcking[2];

    Orpheus()
    {
        name = "Orpheus";
        lv = 1;
        st = 2;
        ma = 2;
        en = 2;
        ag = 2;
        lu = 2;

        myAttcking[0] = &agi;
        myAttcking[1] = &bash;
        attackCount = 2;
        attackSkill = myAttcking;

        affinities[Element::Slash] = Neutral;
        affinities[Element::Strike] = Neutral;
        affinities[Element::Pierce] = Neutral;
        affinities[Element::Fire] = Neutral;
        affinities[Element::Ice] = Neutral;
        affinities[Element::Electricity] = Weak;
        affinities[Element::Wind] = Neutral;
        affinities[Element::Light] = Neutral;
        affinities[Element::Dark] = Weak;
        // add arcana
    }
};
