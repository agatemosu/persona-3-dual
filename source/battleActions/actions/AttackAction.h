#pragma once
#include "ActionBase.h"
#include "../enemies/Enemy.h"
#include "../party/PartyMember.h"
#include <stdio.h>
#include <vector>
#include "../UpdateIndex.h"
#include "../TargetAndAttackEnemy.h"

struct AttackAction : ActionBase
{
    UpdateIndex updateIndex;
    std::vector<BattleParticipant *> *targets;
    PartyMember *user;
    TargetAndAttackActionEnemy *targetAndAttackActionEnemy;

    AttackAction(std::vector<BattleParticipant *> *iTargets, PartyMember *iUser) : targets(iTargets), user(iUser)
    {
        name = "AttackAction";
        possibleUsers = ParticipantType::Party;
        // TODO: dont forget to clear in the future
        targetAndAttackActionEnemy = new TargetAndAttackActionEnemy(targets, user, &targetIndex);
    }

    void execute() override;
    bool update(u32 *keys) override;
};
