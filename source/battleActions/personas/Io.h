#pragma once
#include "PersonaBase.h"

#include "../skills/AttackSkill.h"
#include "../skills/Garu.h"

struct Io : PersonaBase
{
    Garu garu;
    AttackSkill *myAttcking[1];

    Io()
    {
        name = "Io";
        lv = 1;
        st = 2;
        ma = 3;
        en = 1;
        ag = 2;
        lu = 2;

        myAttcking[0] = &garu;
        attackCount = 1;
        attackSkill = myAttcking;

        affinities[Element::Slash] = Neutral;
        affinities[Element::Strike] = Neutral;
        affinities[Element::Pierce] = Neutral;
        affinities[Element::Fire] = Neutral;
        affinities[Element::Ice] = Neutral;
        affinities[Element::Electricity] = Weak;
        affinities[Element::Wind] = Resist;
        affinities[Element::Light] = Neutral;
        affinities[Element::Dark] = Neutral;
        // add arcana
    }
};
