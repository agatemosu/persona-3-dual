#include "core/BaseView.h"
#include <nds/arm9/console.h>
// controllers
#include "controllers/CharacterController.h"
#include "controllers/DialogueController.h"
// environments
#include "environments/iwatodai_dorm.h"
// battle-related
#include "./battleActions/BattleParticipant.h"
#include "./battleActions/BattleStartCondition.h"
#include "./battleActions/enemies/EnemyDb.h"
#include "./controllers/BattleController.h" // TODO: move somewhere

class DebugView : public BaseView
{
  public:
    void init() override;
    ViewState update() override;
    void cleanup() override;
    DebugView();

  private:
    touchPosition touch;

    // sub screen
    int bgMenuHUD;
    PrintConsole console;

    // 3D
    int characterTextureId;
    iwatodai_dorm_Environment iwatodaiDormEnv;

    // init Character Profiles
    CharacterProfiles characterProfiles;
    // Battle participants
    Enemy mercilessMaya = EnemyDb::mercilessMaya;
    Enemy cowardlyMaya = EnemyDb::cowardlyMaya;

    std::vector<BattleParticipant*>* battleParticipants;

    BattleStartCondition battleStartCondition = BattleStartCondition::Even;

    // controllers
    BattleController battleController;
    CharacterController* playerCtrl;
    // camera pos
    cameraPosition camPos;
    // world
    const float tileSize = 0.062500f;
    const float worldOffsetX = IWATODAI_DORM_WORLD_OFFSET_X;
    const float worldOffsetZ = IWATODAI_DORM_WORLD_OFFSET_Z;
    const Point2D<float> characterSize = Point2D<float>(0.1f, 0.1f);
    // movement and viewpoint
    const float speed = 0.02f;
    const float angleIncrement = 0.05f;
    const float distance = 0.7f;
    const float lookAhead = 0.3f;
    // set character initial translation position
    const Point2D<float> characterTranslate = Point2D<float>(0, 0);
    const float height = 0.1f;
    const float angle = -1.6;
    const float characterFacingAngle = 91.67;
    DialogueController dialogueCtrl;
    int bgSharedSlot;
    int totalPolyCount = 0;
    bool isBattleMenuActive = false;
};
