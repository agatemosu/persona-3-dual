#pragma once
#include <calico/types.h>

#define MENU_OPTIONS 7
#define SKILL_OPTIONS 9
#define ITEM_OPTIONS 3
#define EQUIP_OPTIONS 9
#define PERSONA_OPTIONS 3
#define STATS_OPTIONS 9
#define S_LINK_OPTIONS 3
#define SYSTEM_OPTIONS 6

class PauseMenuComponent;
typedef struct
{
    const char* name;
    bool selected;
    int bgIndex = -1;
    void (PauseMenuComponent::*onSelect)();
} PauseOption;

// Menu options
enum {
    SKILL = 0,
    ITEM = 1,
    PERSONA = 2,
    EQUIP = 3,
    STATUS = 4,
    S_LINK = 5,
    SYSTEM = 6
};

// Skill/equip/stats options
enum {
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
enum {
    LIFE_STONE = 0,
    MEDICINE = 1,
    BEAD = 2
};

// Persona options
enum {
    JACK_FROST = 0,
    BLACK_FROST = 1,
    KING_FROST = 2
};

// S.Link options
enum {
    FOOL = 0,
    MAGICIAN = 1,
    EMPEROR = 2
};

// System options
enum {
    TUTORIAL = 0,
    CONFIG = 1,
    DICTIONARY = 2,
    LOAD_DATA = 3,
    SAVE_DATA = 4,
    RETURN_TO_TITLE = 5
};

class PauseMenuComponent {
    private:
        // sfx
        mm_sfxhand sfxMenuHandle;
        mm_sfxhand sfxSelectHandle;
        mm_sfxhand sfxCancelHandle;

        // backgrounds
        int bgSlot = 0;
        void (*bgLoaders[4])(int) = {
            nullptr,
            nullptr,
            nullptr,
            nullptr,
        };

        // options
        PauseOption *options;
        int optionCount;
        int selectedOption = 0;

        PauseOption menuOptions[MENU_OPTIONS] = 
        {
            {"Skill", false, -1, &PauseMenuComponent::openSkillMenu},
            {"Item", false, -1, &PauseMenuComponent::openItemMenu},
            {"Persona", false, -1, &PauseMenuComponent::openPersonaMenu},
            {"Equip", false, -1, &PauseMenuComponent::openEquipMenu},
            {"Status", false, -1, &PauseMenuComponent::openStatusMenu},
            {"S.Link", false, -1, &PauseMenuComponent::openSLinkMenu},
            {"System", false, -1, &PauseMenuComponent::openSystemMenu},
        };

        // TODO: go into submenus
        PauseOption skillOptions[SKILL_OPTIONS] = 
        {
            {"Makoto", false, 0, &PauseMenuComponent::skillOptionSelected},
            {"Yukari", false, 1, &PauseMenuComponent::skillOptionSelected},
            {"Junpei", false, 3, &PauseMenuComponent::skillOptionSelected},
            {"Akihiko", false, 2, &PauseMenuComponent::skillOptionSelected},
            {"Mitsuru", false, -1, &PauseMenuComponent::skillOptionSelected},
            {"Aigis", false, -1, &PauseMenuComponent::skillOptionSelected},
            {"Ken", false, -1, &PauseMenuComponent::skillOptionSelected},
            {"Koromaru", false, -1, &PauseMenuComponent::skillOptionSelected},
            {"Shinjiro", false, -1, &PauseMenuComponent::skillOptionSelected},
        };

        PauseOption itemOptions[ITEM_OPTIONS] = 
        {
            {"Life Stone", false, -1, &PauseMenuComponent::itemOptionSelected},
            {"Medicine", false, -1, &PauseMenuComponent::itemOptionSelected},
            {"Bead", false, -1, &PauseMenuComponent::itemOptionSelected},
        };

        // TODO: go into submenus
        PauseOption equipOptions[EQUIP_OPTIONS] = 
        {
            {"Makoto", false, -1, &PauseMenuComponent::equipOptionSelected},
            {"Yukari", false, -1, &PauseMenuComponent::equipOptionSelected},
            {"Junpei", false, -1, &PauseMenuComponent::equipOptionSelected},
            {"Akihiko", false, -1, &PauseMenuComponent::equipOptionSelected},
            {"Mitsuru", false, -1, &PauseMenuComponent::equipOptionSelected},
            {"Aigis", false, -1, &PauseMenuComponent::equipOptionSelected},
            {"Ken", false, -1, &PauseMenuComponent::equipOptionSelected},
            {"Koromaru", false, -1, &PauseMenuComponent::equipOptionSelected},
            {"Shinjiro", false, -1, &PauseMenuComponent::equipOptionSelected},
        };

        PauseOption personaOptions[PERSONA_OPTIONS] = 
        {
            {"Jack Frot", false, -1, &PauseMenuComponent::personaOptionSelected},
            {"Black Frost", false, -1, &PauseMenuComponent::personaOptionSelected},
            {"King Frost", false, -1, &PauseMenuComponent::personaOptionSelected},
        };

        // TODO: go into submenus
        PauseOption statsOptions[STATS_OPTIONS] = 
        {
            {"Makoto", false, -1, &PauseMenuComponent::statsOptionSelected},
            {"Yukari", false, -1, &PauseMenuComponent::statsOptionSelected},
            {"Junpei", false, -1, &PauseMenuComponent::statsOptionSelected},
            {"Akihiko", false, -1, &PauseMenuComponent::statsOptionSelected},
            {"Mitsuru", false, -1, &PauseMenuComponent::statsOptionSelected},
            {"Aigis", false, -1, &PauseMenuComponent::statsOptionSelected},
            {"Ken", false, -1, &PauseMenuComponent::statsOptionSelected},
            {"Koromaru", false, -1, &PauseMenuComponent::statsOptionSelected},
            {"Shinjiro", false, -1, &PauseMenuComponent::statsOptionSelected},
        };

        // TODO: go into submenus
        PauseOption sLinkOptions[S_LINK_OPTIONS] =
        {
            {"Fool", false, -1, &PauseMenuComponent::sLinkOptionSelected},
            {"Magician", false, -1, &PauseMenuComponent::sLinkOptionSelected},
            {"Emperor", false, -1, &PauseMenuComponent::sLinkOptionSelected},
        };

        // TODO: go into submenus
        PauseOption systemOptions[SYSTEM_OPTIONS] = 
        {
            {"Tutorial", false, -1, &PauseMenuComponent::systemOptionSelected},
            {"Config", false, -1, &PauseMenuComponent::systemOptionSelected},
            {"Dictionary", false, -1, &PauseMenuComponent::systemOptionSelected},
            {"Load Data", false, -1, &PauseMenuComponent::systemOptionSelected},
            {"Save Data", false, -1, &PauseMenuComponent::systemOptionSelected},
            {"Return to Title", false, -1, &PauseMenuComponent::systemOptionSelected},
        };

        void setBgLoaders();
        void loadBg(int bgIndex);

        // OPTION HANDLERS
        // menuOption handlers
        void openSkillMenu();
        void openItemMenu();
        void openPersonaMenu();
        void openEquipMenu();
        void openStatusMenu();
        void openSLinkMenu();
        void openSystemMenu();
        // generic handlers
        void skillOptionSelected();
        void itemOptionSelected();
        void equipOptionSelected();
        void personaOptionSelected();
        void statsOptionSelected();
        void sLinkOptionSelected();
        void systemOptionSelected();

    public:
        void init(int iBgSlot);
        void update(int keys);
        void cancelSFX();
};