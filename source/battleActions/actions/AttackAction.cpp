#include "AttackAction.h"
#include <stdio.h>
#include <string.h>

void AttackAction::execute()
{
    inProgress = true;
    targetIndex = 0;
}

bool AttackAction::update(u32 *keys)
{
    u32 enemyCount = targets->size();

    updateIndex.update(*keys, targetIndex, enemyCount);

    bool madeAction = targetAndAttackActionEnemy->update(keys, user->baseAttackAction);
    if (madeAction)
    {
        targetIndex = 0;
        inProgress = false;
    }

    if (*keys & KEY_B)
    {
        inProgress = false;
    }

    return madeAction;
}
