/*
 * Copyright (C) 2016 The Android Open Source Project
 * Copyright (C) 2026 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <recovery_ui/device.h>
#include <recovery_ui/screen_ui.h>

class NanohubDevice final : public Device {
  public:
    explicit NanohubDevice(RecoveryUI* ui) : Device(ui) {}

    bool PostWipeData() override {
        int fd = open("/sys/class/nanohub/nanohub/erase_shared", O_WRONLY);
        if (fd < 0) {
            printf("error: open erase_shared failed: %s\n", strerror(errno));
            return true;
        }

        static constexpr char kErase[] = "1\n";
        if (write(fd, kErase, sizeof(kErase) - 1) != sizeof(kErase) - 1) {
            printf("error: write to erase_shared failed: %s\n", strerror(errno));
        } else {
            printf("Successfully erased nanoapps.\n");
        }
        close(fd);

        // A persistent permission failure must not create a factory-reset loop.
        return true;
    }
};

extern "C" Device* make_device() {
    return new NanohubDevice(new ScreenRecoveryUI);
}
