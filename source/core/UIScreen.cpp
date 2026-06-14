#include "UIScreen.h"

void UIScreen::moveSprite(int spriteId, int x, int y)
{
    oamSetXY(oam, spriteId, x, y);
}

void UIScreen::showSprite(int spriteId)
{
    oamSetHidden(oam, spriteId, false);
}

void UIScreen::hideSprite(int spriteId)
{
    oamSetHidden(oam, spriteId, true);
}
