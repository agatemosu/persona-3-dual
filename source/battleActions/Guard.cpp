#include "Guard.h"
#include <stdio.h>

void Guard::execute()
{
    inProgress = true;
    iprintf("Guarding\n");
}

bool Guard::update(u32 *keys)
{
    player->guarding = true;
    inProgress = false;
    return true;
}
