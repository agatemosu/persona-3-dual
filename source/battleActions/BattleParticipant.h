#pragma once
#include <nds.h>
#include <vector>
#include "skills/AttackSkill.h"
#include "ParticipantType.h"

struct BattleParticipant
{
    std::string name;
    s32 hp;
    s32 sp;
    u32 lv;
    // TODO: dont think so that all bosses have a basattack, possibly move in the future
    AttackSkill *baseAttackAction;
    ParticipantType participantType;

    BattleStats battleStats;

    std::vector<BattleParticipant *> *battleParticipants;

    bool oneMore = false;
    // knocked will be needed in the future, no use yet
    bool knockedDown = false;

    virtual bool TakeTurn(u32 *keys);

    // for now weel just always use the same flow, but we will sometimes have
    // dialouge during battle in the future
    // unused atm
    virtual void Dialouge();
};
