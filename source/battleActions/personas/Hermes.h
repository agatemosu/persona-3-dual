#pragma once
#include "PersonaBase.h"

#include "../skills/AttackSkill.h"
#include "../skills/Power_Slash.h"

struct Hermes : PersonaBase
{
    Power_Slash power_Slash;
    AttackSkill *myAttcking[1];

    Hermes()
    {
        name = "Hermes";
        lv = 1;
        battleStats.st = 3;
        battleStats.ma = 1;
        battleStats.en = 2;
        battleStats.ag = 3;
        battleStats.lu = 1;

        myAttcking[0] = &power_Slash;
        attackCount = 1;
        attackSkill = myAttcking;

        battleStats.affinities[Element::Slash] = BattleStats::Neutral;
        battleStats.affinities[Element::Strike] = BattleStats::Neutral;
        battleStats.affinities[Element::Pierce] = BattleStats::Neutral;
        battleStats.affinities[Element::Fire] = BattleStats::Resist;
        battleStats.affinities[Element::Ice] = BattleStats::Neutral;
        battleStats.affinities[Element::Electricity] = BattleStats::Neutral;
        battleStats.affinities[Element::Wind] = BattleStats::Weak;
        battleStats.affinities[Element::Light] = BattleStats::Neutral;
        battleStats.affinities[Element::Dark] = BattleStats::Neutral;
        // add arcana
    }
};
