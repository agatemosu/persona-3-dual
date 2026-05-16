#include "core/BaseMenu.h"

#define MAIN_MENU_OPTIONS 3
enum
{
    OPTION_0 = 0,
    OPTION_1,
    OPTION_2
};

class MainMenuComponent : public BaseMenu
{
protected:
    void loadBg(int bgIndex) override;
private:
    MenuOption mainMenuOptions[MAIN_MENU_OPTIONS] =
    {
        {"Option 0", 0, MENU_BIND(MainMenuComponent, mainMenuOptionSelected)},
        {"Option 1", 1, MENU_BIND(MainMenuComponent, mainMenuOptionSelected)},
        {"Option 2", 2, MENU_BIND(MainMenuComponent, mainMenuOptionSelected)},
    };

    // option handlers
    ViewState mainMenuOptionSelected();
public:
    void init(int iBgSlot, bool *isActive) override;
};
