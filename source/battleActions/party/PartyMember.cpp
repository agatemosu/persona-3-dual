#include "PartyMember.h"
#include "../actions/ActionBase.h"
#include <nds.h>
#include <stdio.h>

void PartyMember::Init(std::array<ActionBase*, 4>* iActions)
{
    actions = iActions;
}

bool PartyMember::TakeTurn(u32* keys)
{
    // if an action is already in progress, continue it
    for (u32 i = 0; i < actions->size(); i++)
    {
        ActionBase* action = actions->at(i);
        if (action->inProgress)
        {
            return action->update(keys, this);
        }
    }

    // no action in progress — wait for player to pick one via the battle menu
    // the BattleMenuComponent drives action selection at the view level;
    // here we just check if KEY_LEFT/RIGHT/A were used to select and confirm
    updateIndex.update(*keys, index, actions->size());

    if (*keys & KEY_LEFT || *keys & KEY_RIGHT)
    {
        iprintf("Action: ");
        iprintf(actions->at(index)->name.c_str());
        iprintf("\n");
    }

    if (*keys & KEY_A)
    {
        actions->at(index)->execute();
    }

    return false;
}
