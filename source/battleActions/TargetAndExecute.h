#pragma once
#include <nds.h>
#include <stdio.h>
#include <vector>
#include "BattleParticipant.h"
#include "skills/AttackSkill.h"
#include "skills/HealSkill.h"
#include "skills/Skill.h"
#include "skills/SkillType.h"

// Forward declarations
struct PartyMember;

struct TargetAndExecute
{
    u32 *targetIndex;

    TargetAndExecute(u32 *iTargetIndex) : targetIndex(iTargetIndex) {}

    bool update(u32 *keys, Skill *skill, PartyMember *user, std::vector<BattleParticipant *> *targets)
    {
        if (targets->empty())
            return false;

        // Print current target name
        if (*keys & KEY_LEFT || *keys & KEY_RIGHT)
        {
            iprintf("Target: ");
            iprintf(targets->at(*targetIndex)->name.c_str());
            iprintf("\n");
        }

        if (*keys & KEY_A)
        {
            BattleParticipant *target = targets->at(*targetIndex);

            if (skill->skillType == SkillType::Attack)
            {
                AttackSkill *attackSkill = static_cast<AttackSkill *>(skill);
                u32 accuracy = attackSkill->calculateHitratePlayer(
                    &static_cast<PartyMember *>(user)->curPersona->battleStats,
                    &static_cast<PartyMember *>(target)->curPersona->battleStats);

                bool hit = accuracy > u32(rand() % 100);
                if (!hit)
                {
                    iprintf("missed\n");
                    return true;
                }

                u32 damage = attackSkill->calculateDamagePlayer(
                    &static_cast<PartyMember *>(user)->curPersona->battleStats,
                    &static_cast<PartyMember *>(target)->curPersona->battleStats,
                    &user->lv,
                    &target->lv);

                target->hp -= (s32)damage;
                iprintf("Hit: ");
                iprintf(target->name.c_str());
                char str[50];
                std::sprintf(str, " for %lu dmg\n", (unsigned long)damage);
                iprintf(str);
            }
            else if (skill->skillType == SkillType::Heal)
            {
                HealSkill *healSkill = static_cast<HealSkill *>(skill);
                u32 healing = healSkill->calculateHealing(*user);
                target->hp += (s32)healing;
                iprintf("Healed: ");
                iprintf(target->name.c_str());
                char str[50];
                std::sprintf(str, " for %lu hp\n", (unsigned long)healing);
                iprintf(str);
            }

            return true;
        }

        return false;
    }
};
