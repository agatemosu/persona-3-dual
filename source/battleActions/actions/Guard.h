#pragma once
#include "ActionBase.h"
#include "../party/PartyMember.h"

struct Guard : ActionBase
{
    PartyMember *user;
    Guard(PartyMember *iUser) : user(iUser)
    {
        name = "Guard";
        possibleUsers = ParticipantType::Party;
    }

    void execute() override;
    bool update(u32 *keys) override;
};
