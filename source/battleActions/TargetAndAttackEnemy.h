#pragma once
#include <nds.h>
#include <stdio.h>
#include <vector>
#include "skills/AttackSkill.h"
#include "BattleParticipant.h"
#include "party/PartyMember.h"
#include "DeductAttackCost.h"

struct TargetAndAttackActionEnemy
{

    PartyMember *user;
    std::vector<BattleParticipant *> *targets;
    u32 *targetIndex;

    TargetAndAttackActionEnemy(std::vector<BattleParticipant *> *iTargets, PartyMember *iUser, u32 *iTargetIndex) : targets(iTargets), user(iUser), targetIndex(iTargetIndex) {}

    bool update(u32 *keys, AttackSkill *attack);
};
