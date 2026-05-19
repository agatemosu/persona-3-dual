#pragma once
#include <nds.h>
#include "../ArmourType.h"

// TODO: we need some kind of selection and matching armourType validation outside of battle
// in the future
struct Shoe
{
    u32 evasion = 10;
    ArmourType armourType = ArmourType::Unisex;
    // TODO: add stat boosts / other shenanigans later
};
