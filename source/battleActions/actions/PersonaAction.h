#pragma once
#include <stdio.h>
#include <vector>

#include "ActionBase.h"
#include "../party/PartyMember.h"
#include "../TargetAndAttackEnemy.h"
#include "../UpdateIndex.h"

struct PersonaAction : ActionBase
{
    UpdateIndex updateIndex;
    std::vector<BattleParticipant *> *targets;
    PartyMember *user;
    AttackSkill *selectedSkill;
    TargetAndAttackActionEnemy *targetAndAttackActionEnemy;

    PersonaAction(std::vector<BattleParticipant *> *iTargets, PartyMember *iUser) : targets(iTargets), user(iUser)
    {
        name = "Persona";
        possibleUsers = ParticipantType::Party;

        // TODO: dont forget to clear in the future
        targetAndAttackActionEnemy = new TargetAndAttackActionEnemy(targets, user, &targetIndex);
    }

    //  TargetAndAttackActionEnemy targetAndAttackActionEnemy(player.);

    enum MenuState
    {
        SelectSkill,
        SelectTarget,
    };
    MenuState menuState;

    void execute() override;
    bool update(u32 *keys) override;
};
