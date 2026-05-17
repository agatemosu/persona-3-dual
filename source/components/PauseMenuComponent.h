#pragma once
#include "core/BaseMenu.h"
#include "dialogue/demo_dialogue.h"

#define MENU_OPTIONS 8
#define SKILL_OPTIONS 9
#define ITEM_OPTIONS 3
#define EQUIP_OPTIONS 9
#define PERSONA_OPTIONS 3
#define STATS_OPTIONS 9
#define S_LINK_OPTIONS 3
#define SYSTEM_OPTIONS 6
#define DEBUG_OPTIONS 10
#define CHARACTER_ANIM_OPTIONS 25
#define SKILLS 2

// Menu options
enum
{
    SKILL = 0,
    ITEM = 1,
    PERSONA = 2,
    EQUIP = 3,
    STATUS = 4,
    S_LINK = 5,
    SYSTEM = 6
};

// Skill/equip/stats options
enum
{
    MAKOTO = 0,
    YUKARI = 1,
    JUNPEI = 2,
    AKIHIKO = 3,
    MITSURU = 4,
    AIGIS = 5,
    KEN = 6,
    KOROMARU = 7,
    SHINJIRO = 8
};

// Item options
enum
{
    LIFE_STONE = 0,
    MEDICINE = 1,
    BEAD = 2
};

// Persona options
enum
{
    JACK_FROST = 0,
    BLACK_FROST = 1,
    KING_FROST = 2
};

// S.Link options
enum
{
    FOOL = 0,
    MAGICIAN = 1,
    EMPEROR = 2
};

// System options
enum
{
    TUTORIAL = 0,
    CONFIG = 1,
    DICTIONARY = 2,
    LOAD_DATA = 3,
    SAVE_DATA = 4,
    RETURN_TO_TITLE = 5
};

// Debug options
enum
{
    DISCLAIMER_VIEW = 0,
    INTRO_VIDEO_VIEW = 1,
    INTRO_VIEW = 2,
    MAIN_MENU_VIEW = 3,
    IWATODAI_DORM_VIEW = 4,
    IWATODAI_STREETS_VIEW = 5,
    DEBUG_DIALOGUE = 6,
    TOGGLE_BILLBOARDS = 7,
    TOGGLE_DEBUG_PRINT = 8,
    PLAY_CHARACTER_ANIM = 9
};

// Character animation options
enum
{
    TOGGLE_AUTO_ANIM = 0,
    ANIM_1 = 1,
    ANIM_2 = 2,
    ANIM_3 = 3,
    ANIM_4 = 4,
    ANIM_5 = 5,
    ANIM_6 = 6,
    ANIM_7 = 7,
    ANIM_8 = 8,
    ANIM_9 = 9,
    ANIM_10 = 10,
    ANIM_11 = 11,
    ANIM_12 = 12,
    ANIM_13 = 13,
    ANIM_14 = 14,
    ANIM_15 = 15,
    ANIM_16 = 16,
    ANIM_17 = 17,
    ANIM_18 = 18,
    ANIM_19 = 19,
    ANIM_20 = 20,
    ANIM_21 = 21,
    ANIM_22 = 22,
    ANIM_23 = 23,
    ANIM_24 = 24
};

class PauseMenuComponent : public BaseMenu
{
protected:
    void loadBg(int bgIndex) override;

private:
    MenuOption menuOptions[MENU_OPTIONS] =
    {
        {"Debug",   -1, MENU_BIND(PauseMenuComponent, openDebugMenu)},
        {"Skill",   -1, MENU_BIND(PauseMenuComponent, openSkillMenu)},
        {"Item",    -1, MENU_BIND(PauseMenuComponent, openItemMenu)},
        {"Persona", -1, MENU_BIND(PauseMenuComponent, openPersonaMenu)},
        {"Equip",   -1, MENU_BIND(PauseMenuComponent, openEquipMenu)},
        {"Status",  -1, MENU_BIND(PauseMenuComponent, openStatusMenu)},
        {"S.Link",  -1, MENU_BIND(PauseMenuComponent, openSLinkMenu)},
        {"System",  -1, MENU_BIND(PauseMenuComponent, openSystemMenu)},
    };

    MenuOption debugOptions[DEBUG_OPTIONS] =
    {
        {"DisclaimerView",            -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"IntroVideoView",            -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"IntroView",                 -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"MainMenuView",              -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"IwatodaiDormView",          -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"IwatodaiStreetView",        -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"Debug Dialogue",            -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"Toggle Billboards",         -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"Toggle Debug Print",        -1, MENU_BIND(PauseMenuComponent, debugOptionSelected)},
        {"Play Character Animations", -1, MENU_BIND(PauseMenuComponent, openCharacterAnimMenu)},
    };

    MenuOption skillOptions[SKILL_OPTIONS] =
    {
        {"Makoto",   0, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
        {"Yukari",   1, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
        {"Junpei",   3, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
        {"Akihiko",  2, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
        {"Mitsuru", -1, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
        {"Aigis",   -1, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
        {"Ken",     -1, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
        {"Koromaru",-1, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
        {"Shinjiro",-1, MENU_BIND(PauseMenuComponent, skillOptionSelected)},
    };

    MenuOption itemOptions[ITEM_OPTIONS] =
    {
        {"Life Stone", -1, MENU_BIND(PauseMenuComponent, itemOptionSelected)},
        {"Medicine",   -1, MENU_BIND(PauseMenuComponent, itemOptionSelected)},
        {"Bead",       -1, MENU_BIND(PauseMenuComponent, itemOptionSelected)},
    };

    MenuOption equipOptions[EQUIP_OPTIONS] =
    {
        {"Makoto",   -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
        {"Yukari",   -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
        {"Junpei",   -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
        {"Akihiko",  -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
        {"Mitsuru",  -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
        {"Aigis",    -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
        {"Ken",      -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
        {"Koromaru", -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
        {"Shinjiro", -1, MENU_BIND(PauseMenuComponent, equipOptionSelected)},
    };

    MenuOption personaOptions[PERSONA_OPTIONS] =
    {
        {"Jack Frost",  -1, MENU_BIND(PauseMenuComponent, personaOptionSelected)},
        {"Black Frost", -1, MENU_BIND(PauseMenuComponent, personaOptionSelected)},
        {"King Frost",  -1, MENU_BIND(PauseMenuComponent, personaOptionSelected)},
    };

    MenuOption statsOptions[STATS_OPTIONS] =
    {
        {"Makoto",   -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
        {"Yukari",   -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
        {"Junpei",   -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
        {"Akihiko",  -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
        {"Mitsuru",  -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
        {"Aigis",    -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
        {"Ken",      -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
        {"Koromaru", -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
        {"Shinjiro", -1, MENU_BIND(PauseMenuComponent, statsOptionSelected)},
    };

    MenuOption sLinkOptions[S_LINK_OPTIONS] =
    {
        {"Fool",     -1, MENU_BIND(PauseMenuComponent, sLinkOptionSelected)},
        {"Magician", -1, MENU_BIND(PauseMenuComponent, sLinkOptionSelected)},
        {"Emperor",  -1, MENU_BIND(PauseMenuComponent, sLinkOptionSelected)},
    };

    MenuOption systemOptions[SYSTEM_OPTIONS] =
    {
        {"Tutorial",        -1, MENU_BIND(PauseMenuComponent, systemOptionSelected)},
        {"Config",          -1, MENU_BIND(PauseMenuComponent, systemOptionSelected)},
        {"Dictionary",      -1, MENU_BIND(PauseMenuComponent, systemOptionSelected)},
        {"Load Data",       -1, MENU_BIND(PauseMenuComponent, systemOptionSelected)},
        {"Save Data",       -1, MENU_BIND(PauseMenuComponent, systemOptionSelected)},
        {"Return to Title", -1, MENU_BIND(PauseMenuComponent, systemOptionSelected)},
    };

    MenuOption skills[SKILLS] =
    {
        {"Skill 1", -1, nullptr},
        {"Skill 2", -1, nullptr},
    };

    MenuOption characterAnimOptions[CHARACTER_ANIM_OPTIONS] =
    {
        {"Toggle Auto Animations", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0000", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0001", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0002", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0003", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0004", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0005", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0006", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0007", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0008", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0009", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0010", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0011", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0012", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0013", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0014", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0015", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0016", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0017", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0018", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0019", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0020", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0021", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"0022", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
        {"root", -1, MENU_BIND(PauseMenuComponent, characterAnimOptionSelected)},
    };

    // menu navigation handlers
    ViewState openDebugMenu();
    ViewState openSkillMenu();
    ViewState openItemMenu();
    ViewState openPersonaMenu();
    ViewState openEquipMenu();
    ViewState openStatusMenu();
    ViewState openSLinkMenu();
    ViewState openSystemMenu();
    ViewState openCharacterAnimMenu();

    // selection handlers
    ViewState debugOptionSelected();
    ViewState skillOptionSelected();
    ViewState itemOptionSelected();
    ViewState equipOptionSelected();
    ViewState personaOptionSelected();
    ViewState statsOptionSelected();
    ViewState sLinkOptionSelected();
    ViewState systemOptionSelected();
    ViewState characterAnimOptionSelected();

public:
    void init(int iBgSlot, bool *isActive) override;
    ViewState update(int keys) override;
};
