#pragma once
#include "../ArmourType.h"
#include "../BattleParticipant.h"
#include "../ParticipantType.h"
#include "../UpdateIndex.h"
#include "../armours/Armour.h"
#include "../personas/PersonaBase.h"
#include "../shoes/Shoe.h"
#include "CharacterProfile.h"
#include <array>
#include <nds.h>

struct ActionBase;

struct PartyMember : BattleParticipant
{
    UpdateIndex updateIndex;
    u32 index = 0;

    Armour armour;
    Shoe shoe;
    std::vector<PersonaBase*> personas;
    PersonaBase* curPersona;

    bool guarding = false;

    CharacterProfile* characterProfile;

    bool canUseAction[4];
    std::array<ActionBase*, 4>* actions = nullptr;

    PartyMember(CharacterProfile* iCharacterProfile) : characterProfile(iCharacterProfile)
    {
        name = characterProfile->name;
        maxHp = characterProfile->maxHp;
        hp = characterProfile->hp;
        maxSp = characterProfile->maxSp;
        sp = characterProfile->sp;
        lv = characterProfile->lv;

        baseAttackAction = characterProfile->baseAttackAction;
        participantType = characterProfile->participantType;

        armour = characterProfile->armour;
        personas = characterProfile->personas;
        curPersona = characterProfile->curPersona;
    }
    ~PartyMember() {};

    void Init(std::array<ActionBase*, 4>* iActions);
    bool TakeTurn(u32* keys) override;
};
