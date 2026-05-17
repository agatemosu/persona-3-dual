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
        battleStats.st = 2;
        battleStats.ma = 3;
        battleStats.en = 1;
        battleStats.ag = 2;
        battleStats.lu = 2;

        myAttcking[0] = &garu;
        attackCount = 1;
        attackSkill = myAttcking;

        battleStats.affinities[Element::Slash] = BattleStats::Neutral;
        battleStats.affinities[Element::Strike] = BattleStats::Neutral;
        battleStats.affinities[Element::Pierce] = BattleStats::Neutral;
        battleStats.affinities[Element::Fire] = BattleStats::Neutral;
        battleStats.affinities[Element::Ice] = BattleStats::Neutral;
        battleStats.affinities[Element::Electricity] = BattleStats::Weak;
        battleStats.affinities[Element::Wind] = BattleStats::Resist;
        battleStats.affinities[Element::Light] = BattleStats::Neutral;
        battleStats.affinities[Element::Dark] = BattleStats::Neutral;
        // add arcana
    }
};
