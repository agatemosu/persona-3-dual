#include "TargetAndAttackEnemy.h"

bool TargetAndAttackActionEnemy::update(u32 *keys, AttackSkill *attack)
{
    if (*keys & KEY_LEFT)
    {
        iprintf("CurTar: ");
        iprintf(enemies->at(*targetIndex)->name.c_str());
        iprintf("\n");
    }
    else if (*keys & KEY_RIGHT)
    {
        iprintf("CurTar: ");
        iprintf(enemies->at(*targetIndex)->name.c_str());
        iprintf("\n");
    }

    if (*keys & KEY_A)
    {
        iprintf("Attacking: ");
        iprintf(enemies->at(*targetIndex)->name.c_str());
        iprintf("\n");

        u32 damage = attack->calculateDamage(player->curPersona->getBattleStats(), enemies->at(*targetIndex)->getBattleStats(), &player->lv, &enemies->at(*targetIndex)->lv);
        enemies->at(*targetIndex)->hp -= damage;

        char str1[25];
        std::sprintf(str1, "Damage: %lu \n", damage);
        iprintf(str1);

        char str2[50];
        std::sprintf(str2, "remaing Enemy hp: %lu \n", enemies->at(*targetIndex)->hp);
        iprintf(str2);

        return true;
    }

    return false;
}
