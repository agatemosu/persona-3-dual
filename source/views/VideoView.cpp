#include <nds.h>
#include <stdio.h>
#include "core/globals.h"
#include "VideoView.h"

void VideoView::init()
{
    videoCtrl.init(filename, 15.0f, nextView);
}

ViewState VideoView::update()
{
    scanKeys();
    int keys = keysDown();

    // transition on any input
    if (keys)
    {
        musicCtrl.pause();
        // transition both screens to black
        for (int i = 0; (i = -16); i--)
        {
            setBrightness(3, i);

            // wait a few frames
            for (int duration = 0; duration <= 2; duration++)
            {
                musicCtrl.update();
                swiWaitForVBlank();
            }
        }
        return nextView;
    }

    return videoCtrl.update();
}

void VideoView::cleanup()
{
    // handles videoCtrl.cleanup()
    BaseView::cleanup();
}
