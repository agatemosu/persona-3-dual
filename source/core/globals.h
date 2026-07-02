#pragma once
#include "core/structs.h"
#include <string>

// variables
extern volatile int frame;
extern int fps;
extern int fpsTimer;
extern std::string fatBasePath;
extern Save saveData;
extern unsigned int** bitmapsCharacter;

// components
extern bool enableBillboards;
extern bool enableDebugPrint;
extern bool enableCharacterAnim;
extern bool isPauseMenuActive;
