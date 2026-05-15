#pragma once
#include "PartyMember.h"
#include "../armours/RashGuard.h"
#include "../personas/Io.h"
#include "../skills/Pierce_Attack.h"

struct Yukari : PartyMember
{
    RashGuard rashGuard;
    Pierce_Attack pierce_Attack;
    Io io;

    Yukari()
    {
        name = "Yukari";
        hp = 720;
        sp = 50;
        lv = 2;

        armourType = ArmourType::Female;
        armour = rashGuard;

        baseAttackAction = &pierce_Attack;
        persona = &io;
    }
};
