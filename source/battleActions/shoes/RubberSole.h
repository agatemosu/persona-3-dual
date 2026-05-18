#pragma once
#include "shoe.h"

struct RubberSole : Shoe
{
    RubberSole()
    {
        evasion = 19;
        armourType = ArmourType::Unisex;
    }
};
