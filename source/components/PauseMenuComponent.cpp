#include <nds.h>
#include "core/globals.h"
#include "PauseMenuComponent.h"

// sfx
#include "soundbank.h"

// backgrounds
#include "bgYukiClose.h"
#include "bgGuard.h"
#include "bgAkihiko.h"
#include "bgYuki.h"

// add background setup here, and assign the bgLoader index to the appropriate PauseOption in PauseMenuComponent.h
void PauseMenuComponent::setBgLoaders()
{
    bgLoaders[0] = [](int slot)
    {
        dmaCopy(bgGuardTiles, bgGetGfxPtr(slot), bgGuardTilesLen);
        dmaCopy(bgGuardMap, bgGetMapPtr(slot), bgGuardMapLen);
        vramSetBankH(VRAM_H_LCD);
        dmaCopy(bgGuardPal, &VRAM_H_EXT_PALETTE[0][0], bgGuardPalLen);
        vramSetBankH(VRAM_H_SUB_BG_EXT_PALETTE);
        bgShow(slot);
    };
    bgLoaders[1] = [](int slot)
    {
        dmaCopy(bgYukiTiles, bgGetGfxPtr(slot), bgYukiTilesLen);
        dmaCopy(bgYukiMap, bgGetMapPtr(slot), bgYukiMapLen);
        vramSetBankH(VRAM_H_LCD);
        dmaCopy(bgYukiPal, &VRAM_H_EXT_PALETTE[0][0], bgYukiPalLen);
        vramSetBankH(VRAM_H_SUB_BG_EXT_PALETTE);
        bgShow(slot);
    };
    bgLoaders[2] = [](int slot)
    {
        dmaCopy(bgAkihikoTiles, bgGetGfxPtr(slot), bgAkihikoTilesLen);
        dmaCopy(bgAkihikoMap, bgGetMapPtr(slot), bgAkihikoMapLen);
        vramSetBankH(VRAM_H_LCD);
        dmaCopy(bgAkihikoPal, &VRAM_H_EXT_PALETTE[0][0], bgAkihikoPalLen);
        vramSetBankH(VRAM_H_SUB_BG_EXT_PALETTE);
        bgShow(slot);
    };
    bgLoaders[3] = [](int slot)
    {
        dmaCopy(bgYukiCloseTiles, bgGetGfxPtr(slot), bgYukiCloseTilesLen);
        dmaCopy(bgYukiCloseMap, bgGetMapPtr(slot), bgYukiCloseMapLen);
        vramSetBankH(VRAM_H_LCD);
        dmaCopy(bgYukiClosePal, &VRAM_H_EXT_PALETTE[0][0], bgYukiClosePalLen);
        vramSetBankH(VRAM_H_SUB_BG_EXT_PALETTE);
        bgShow(slot);
    };
}

void PauseMenuComponent::loadBg(int bgIndex)
{
    if (bgIndex >= 0 && bgIndex < 4 && bgLoaders[bgIndex])
        bgLoaders[bgIndex](bgSlot);
}

void PauseMenuComponent::cancelSFX()
{
    musicCtrl.stopSFX(sfxMenuHandle);
    musicCtrl.stopSFX(sfxSelectHandle);
    musicCtrl.stopSFX(sfxCancelHandle);
}

void PauseMenuComponent::init(int iBgSlot)
{
    // point to music
    musicCtrl.loadSFX(SFX_MENU);
    musicCtrl.loadSFX(SFX_SELECT);
    musicCtrl.loadSFX(SFX_CANCEL);

    // set default options
    options = menuOptions;
    optionCount = MENU_OPTIONS;

    // set bg loaders
    bgSlot = iBgSlot;
    setBgLoaders();
}

void PauseMenuComponent::update(int keys)
{
    // navigate options
    if (keys & KEY_DOWN)
    {
        sfxMenuHandle = musicCtrl.playSFX(SFX_MENU, 255, 128);
        selectedOption = (selectedOption + 1) % optionCount;
    }

    if (keys & KEY_UP)
    {
        sfxMenuHandle = musicCtrl.playSFX(SFX_MENU, 255, 128);
        selectedOption = (selectedOption + optionCount - 1) % optionCount;
    }

    if (keys & KEY_A)
    {
        cancelSFX();
        sfxSelectHandle = musicCtrl.playSFX(SFX_SELECT, 255, 128);

        PauseState currentState = {options, optionCount, selectedOption};

        if (options[selectedOption].onSelect != nullptr) {
            (this->*(options[selectedOption].onSelect))();
            if (options != currentState.options) { // if we changed options, push current state to stack
                prevOptions.push(currentState);
            }
        }
    }

    if (keys & KEY_B)
    {
        cancelSFX();
        musicCtrl.playSFX(SFX_CANCEL, 255, 128);

        selectedOption = 0;

        // if we're in a submenu, return to main menu
        if (!prevOptions.empty())
        {
            PauseState prevState = prevOptions.top();
            prevOptions.pop();

            options = prevState.options;
            optionCount = prevState.optionCount;
            selectedOption = prevState.selectedOption;
        }
    }

    consoleClear();

    printf("\x1b[0;0H");

    // blink the "Pause" text
    if (frame % 60 < 30)
    {
        iprintf("Pause\n");
    }
    else
    {
        iprintf("\n");
    }

    // display options
    for (int option = 0; option < optionCount; option++)
    {
        iprintf("%c %s\n", option == selectedOption ? '>' : ' ', options[option].name);
    }

    // load selectedOption's background
    int bgIndex = options[selectedOption].bgIndex;
    if (bgIndex != -1)
    {
        loadBg(bgIndex);
        bgShow(bgSlot);
    }
    else
    {
        bgHide(bgSlot);
    }

    return;
}

// OPTION HANDLERS
// menuOption handlers
void PauseMenuComponent::openSkillMenu()
{
    selectedOption = 0;
    options = skillOptions;
    optionCount = SKILL_OPTIONS;
}

void PauseMenuComponent::openItemMenu()
{
    selectedOption = 0;
    options = itemOptions;
    optionCount = ITEM_OPTIONS;
}

void PauseMenuComponent::openPersonaMenu()
{
    selectedOption = 0;
    options = personaOptions;
    optionCount = PERSONA_OPTIONS;
}

void PauseMenuComponent::openEquipMenu()
{
    selectedOption = 0;
    options = equipOptions;
    optionCount = EQUIP_OPTIONS;
}

void PauseMenuComponent::openStatusMenu()
{
    selectedOption = 0;
    options = statsOptions;
    optionCount = STATS_OPTIONS;
}

void PauseMenuComponent::openSLinkMenu()
{
    selectedOption = 0;
    options = sLinkOptions;
    optionCount = S_LINK_OPTIONS;
}

void PauseMenuComponent::openSystemMenu()
{
    selectedOption = 0;
    options = systemOptions;
    optionCount = SYSTEM_OPTIONS;
}

// generic handlers
// this is where we would implement functionality for going into a sub-menu, or selecting a skill, item, etc.
void PauseMenuComponent::skillOptionSelected()
{
    selectedOption = 0;
    options = skills;
    optionCount = SKILLS;
}

void PauseMenuComponent::itemOptionSelected()
{
    // ...
}

void PauseMenuComponent::equipOptionSelected()
{
    // ...
}

void PauseMenuComponent::personaOptionSelected()
{
    // ...
}

void PauseMenuComponent::statsOptionSelected()
{
    // ...
}

void PauseMenuComponent::sLinkOptionSelected()
{
    // ...
}

void PauseMenuComponent::systemOptionSelected()
{
    // ...
}