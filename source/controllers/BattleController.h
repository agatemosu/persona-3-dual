#pragma once

#include <stdio.h>
#include <nds.h>
#include <stdio.h>
#include <vector>

#include "./battleActions/BattleParticipant.h"
#include "./battleActions/enemies/Enemy.h"
#include "./battleActions/party/PartyMember.h"

class BattleController
{
private:
    u32 turnsTaken = 0;
    BattleParticipant *currentParticipantTurn;
    bool active = false;
    bool isEnemyTurn = false;

    std::vector<BattleParticipant *> *battleParticipants;
    // needs to be battleparticipant so i can just vecotr push back based on participant type alone
    std::vector<BattleParticipant *> *enemies;
    std::vector<BattleParticipant *> *partyMembers;

    void enemyTurn();

public:
    bool isActive() { return active; };
    void execute();
    void update(u32 keys);
    void exit();
    BattleController(std::vector<BattleParticipant *> *iBattleParticipants);
    ~BattleController() {}
};
