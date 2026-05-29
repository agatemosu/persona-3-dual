#pragma once
#include <nds.h>
#include <vector>
#include "../skills/AttackSkill.h"
#include "../ParticipantType.h"
#include "../shoes/Shoe.h"
#include "../personas/PersonaBase.h"

struct CharacterProfile
{
    std::string name;
    s32 maxHp;
    s32 hp;
    s32 maxSp;
    s32 sp;
    u32 lv;
    ParticipantType participantType;

    ArmourType armourType;
    Armour armour;
    Shoe shoe;

    AttackSkill *baseAttackAction;
    std::vector<PersonaBase *> personas;

    PersonaBase *curPersona;
};
