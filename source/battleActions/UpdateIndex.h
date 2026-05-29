#pragma once
#include <nds.h>

struct UpdateIndex
{
    void update(u32 keys, u32& index, size_t size)
    {
        if (size == 0)
            return;

        if (keys & KEY_RIGHT)
        {
            index = (index + 1) % size;
        }
        else if (keys & KEY_LEFT)
        {
            index = (index + size - 1) % size;
        }
    }
};
