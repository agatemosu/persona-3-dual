#pragma once
#include <nds.h>
#include <stack>
#include "core/globals.h"
#include "core/structs.h"

#define MENU_BIND(ClassName, Method) static_cast<ViewState (BaseMenu::*)()>(&ClassName::Method)

class BaseMenu
{
protected:
    bool *isActivePtr;
    int bgSlot = 0;

    // options
    MenuOption *options;
    int optionCount = 0;
    int selectedOption = 0;
    int startIndex = 0;

    virtual void loadBg(int bgIndex) = 0;
private:
    // sfx
    mm_sfxhand sfxMenuHandle;
    mm_sfxhand sfxSelectHandle;
    mm_sfxhand sfxCancelHandle;

    // options
    int visibleOptions = 23;
    stack<MenuState> prevOptions;
    ViewState nextViewState = ViewState::KEEP_CURRENT;
public:
    virtual void init(int iBgSlot, bool *isActive);
    virtual ViewState update(int keys);
    void cancelSFX();
    ViewState changeMenu(MenuOption* newOptions, int newOptionCount);
};
