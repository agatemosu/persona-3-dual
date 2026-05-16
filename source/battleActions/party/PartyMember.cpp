#include "PartyMember.h"

void PartyMember::Init(std::vector<BattleParticipant *> *iBattleParticipant, std::array<ActionBase *, 4> *iActions)
{
    battleParticipants = iBattleParticipant;
    actions = iActions;
    if (participantType == ParticipantType::Player)
    {
        for (int i = 0; i < actions->size(); i++)
        {
            actions->at(i)->canUse = true;
        }
    }
    else if (participantType == ParticipantType::Party)
    {
        for (int i = 0; i < actions->size(); i++)
        {
            if (actions->at(i)->possibleUsers == ParticipantType::Party)
            {
                actions->at(i)->canUse = true;
            }
            else
            {
                actions->at(i)->canUse = false;
            }
        }
    }
}

bool PartyMember::TakeTurn(u32 *keys)
{
    u32 actionCount = actions->size();
    for (u32 i = 0; i < actionCount; i++)
    {
        if (actions->at(i)->inProgress)
        {
            return actions->at(i)->update(keys);
        }
    }

    updateIndex.update(*keys, index, actionCount);

    if (*keys & KEY_LEFT || *keys & KEY_RIGHT)
    {
        iprintf("Cur: ");
        iprintf(actions->at(index)->name.c_str());
        iprintf("\n");
    }

    if (*keys & KEY_A && actions->at(index)->canUse)
    {
        actions->at(index)->execute();
    }
}
