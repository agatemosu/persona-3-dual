#include "Enemy.h"
#include "../battleActions/DeductAttackCost.h"

bool Enemy::TakeTurn(u32 *keys)
{
    u32 randomNum = rand() % attackCount + 1;

    u8 potentialTargetsCount = 0;
    for (int i = 0; i < battleParticipants->size(); i++)
    {
        if (battleParticipants->at(i)->participantType == ParticipantType::Party || battleParticipants->at(i)->participantType == ParticipantType::Player)
            potentialTargetsCount++;
    }

    u8 target = rand() % potentialTargetsCount;

    u32 damage;
    AttackSkill *curSkill;

    // TODO: enemy ai. ugly way but this is temporary anyway since we dont have any actuall ai yet
    if (randomNum == 0)
    {
        curSkill = baseAttackAction;
        damage = curSkill->calculateDamageEnemyRegular(battleStats.getBattleStats(), player->curPersona->getBattleStats(), &enemies->at(counter)->lv, &player->lv, &player->armour);
    }
    else
    {
        curSkill = enemies->at(counter)->attackSkill[randomNum - 1];
        damage = curSkill->calculateDamageEnemySkill(enemies->at(counter)->getBattleStats(), player->curPersona->getBattleStats(), &enemies->at(counter)->lv, &player->lv, &player->armour);
    }

    if (player->guarding)
    {
        iprintf("player guarded\n");
        damage *= 0.4;
    }

    bool attacked = false;
    if (curSkill->race == AttackSkill::mag)
    {
        if (!DeductAttackCost(&enemies->at(counter)->sp, curSkill->cost, "not enough SP\n"))
        {
            counter++;
        }
        else
        {
            attacked = true;
        }
    }
    else if (curSkill->race == AttackSkill::phys)
    {
        if (!DeductAttackCost(&enemies->at(counter)->hp, curSkill->cost, "not enough HP\n"))
        {
            counter++;
        }
        else
        {
            attacked = true;
        }
    }

    if (attacked)
    {
        player->hp -= (s32)damage;
        iprintf("Attack with: ");
        iprintf(curSkill->name.c_str());
        iprintf("\n");
        char str[50];
        std::sprintf(str, "remaining player hp: %ld \n", player->hp);
        iprintf(str);
        if (player->hp <= 0)
        {
            player->hp = 72;
            counter = 0;
            exit();
            return;
        }

        u32 affinity = player->curPersona->affinities[curSkill->element];
        if (affinity == BattleStats::Affinity::Weak && !player->knockedDown && !player->guarding)
        {
            enemies->at(counter)->oneMore = true;
            iprintf("one more!\n");
            player->knockedDown = true;
        }

        if (!enemies->at(counter)->oneMore)
        {
            counter++;
        }
        else
        {
            enemies->at(counter)->oneMore = false;
        }
    }

    if (counter >= enemies->size())
    {
        player->guarding = false;
        if (player->knockedDown)
        {
            // recovery logic in the future
            player->knockedDown = false;
        }
        isEnemyTurn = false;
        counter = 0;
    }
}
