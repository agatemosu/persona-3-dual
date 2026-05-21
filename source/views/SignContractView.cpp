#include <nds.h>
#include <stdio.h>
#include "core/globals.h"
#include "core/enums.h"
#include "SignContractView.h"

// assets
#include "contract.h"
// sfx
#include "soundbank.h"


void SignContractView::cancelSFX()
{
    musicCtrl.stopSFX(sfxMenuHandle);
    musicCtrl.stopSFX(sfxSelectHandle);
    musicCtrl.stopSFX(sfxCancelHandle);
}

void SignContractView::init()
{
    // set both screens to black
    setBrightness(3, -16);

    // setup music
    musicCtrl.loadSFX(SFX_MENU);
    musicCtrl.loadSFX(SFX_SELECT);
    musicCtrl.loadSFX(SFX_CANCEL);
    musicCtrl.init((fatBasePath + "music/mistic.pcm").c_str(), 0.0f, -1.0f);

    videoSetMode(MODE_5_2D);
    videoSetModeSub(MODE_0_2D);

    // map vram banks to main engine background
    vramSetBankA(VRAM_A_MAIN_BG_0x06000000);
    vramSetBankD(VRAM_D_MAIN_BG_0x06020000);
    // map vram to sub screen
    vramSetBankC(VRAM_C_SUB_BG);

    // enable extended palettes
    bgExtPaletteEnable();

    // initialize backgrounds
    bg[0] = bgInit(0, BgType_Text8bpp, BgSize_T_256x256, 9, 2);
    bgSetPriority(bg[0], 0);

    // set backgrounds
    dmaFillHalfWords(0, bgGetMapPtr(bg[0]), 8192);
    dmaCopy(contractTiles, bgGetGfxPtr(bg[0]), contractTilesLen);
    dmaCopy(contractMap, bgGetMapPtr(bg[0]), contractMapLen);

    vramSetBankE(VRAM_E_LCD);
    dmaCopy(contractPal, &VRAM_E_EXT_PALETTE[0][0], contractPalLen);
    vramSetBankE(VRAM_E_BG_EXT_PALETTE);

    // setup console
    consoleInit(&console, 0, BgType_Text4bpp, BgSize_T_256x256, 2, 0, false, true);
    consoleSelect(&console);
    keyboardInit(&keyboard, 1, BgType_Text4bpp, BgSize_T_256x512, 3, 1, false, true);
    bgSetPriority(console.bgId, 0);
    bgSetPriority(keyboard.background, 1);
    keyboardShow();

    iprintf("\x1b[11;6HEnter your last name");
    iprintf("\x1b[0;0H");

    // transition both screens from black
    for (int i = -16; i < 0; i++)
    {
        setBrightness(3, i);

        // wait a few frames
        for (int duration = 0; duration <= 2; duration++)
        {
            swiWaitForVBlank();
            musicCtrl.update();
        }
    }
}

ViewState SignContractView::update()
{
    scanKeys();
    int key = keyboardUpdate();
    int pressed = keysDown();

    // Bksp (8) or "B"
    if ((key == 8) || (pressed & KEY_B))
    {
        key = 8;
        cancelSFX();
        sfxCancelHandle = musicCtrl.playSFX(SFX_CANCEL, 255, 128);

        if (isLastName)
        {
            if (!lastName.empty())
            {
                lastName.pop_back();
                iprintf("%c", key);
            }
        }
        else if (!isLastName && !isNameConfirmed)
        {
            if (firstName.empty())
            {
                isLastName = true;
                consoleClear();
                iprintf("\x1b[11;6HEnter your last name");
                iprintf("\x1b[0;0H%s", lastName.c_str());
            } else
            {
                firstName.pop_back();
                iprintf("%c", key);
            }
        }
        else
        {
            isNameConfirmed = false;
            consoleClear();
            iprintf("\x1b[11;6HEnter your first name");
            iprintf("\x1b[0;0H%s", firstName.c_str());
        }
    }
    // Return (10) or "A"
    else if ((key == 10) || (pressed & KEY_A))
    {
        key = 10;
        cancelSFX();
        sfxSelectHandle = musicCtrl.playSFX(SFX_SELECT, 255, 128);

        if (isLastName)
        {
            isLastName = false;
            consoleClear();
            iprintf("\x1b[11;5HEnter your first name");
            iprintf("\x1b[0;0H");
        }
        else if (!isNameConfirmed)
        {
            isNameConfirmed = true;
            consoleClear();
            iprintf("\x1b[11;7HConfirm your name?");

            // center the text
            int posLastName = 15 - (lastName.length()/2);
            int posFirstName = 15 - (firstName.length()/2);

            iprintf("\x1b[8;%iH%s,", posLastName, lastName.c_str());
            iprintf("\x1b[9;%iH%s", posFirstName, firstName.c_str());
        }
        else
        {
            cancelSFX();
            // transition both screens to black
            for (int i = 0; i <= 16; i++)
            {
                setBrightness(3, -i);

                // wait a few frames
                for (int duration = 0; duration <= 2; duration++)
                {
                    swiWaitForVBlank();
                    musicCtrl.update();
                }
            }
            musicCtrl.pause();

            return ViewState::CUTSCENE_2;
        }
    }
    // on any other keyboard entry
    else if (key > 0)
    {
        cancelSFX();
        sfxMenuHandle = musicCtrl.playSFX(SFX_MENU, 255, 128);

        if (isLastName)
        {
            lastName.push_back(key);
        }
        else
        {
            firstName.push_back(key);
        }

        iprintf("%c", key);
    }

    musicCtrl.update();
    return ViewState::KEEP_CURRENT;
}

void SignContractView::cleanup()
{
    BaseView::cleanup();
}
