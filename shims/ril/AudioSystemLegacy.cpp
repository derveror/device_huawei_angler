// SPDX-FileCopyrightText: 2020 The LineageOS Project
// SPDX-FileCopyrightText: 2026 The LineageOS Project
// SPDX-License-Identifier: Apache-2.0

#include <media/AudioSystem.h>

extern "C" uintptr_t currentAddErrorCallback(android::audio_error_callback callback)
        __asm__("_ZN7android11AudioSystem16addErrorCallbackEPFviE");

extern "C" void legacySetErrorCallback(android::audio_error_callback callback)
        __asm__("_ZN7android11AudioSystem16setErrorCallbackEPFviE");

void legacySetErrorCallback(android::audio_error_callback callback) {
    (void)currentAddErrorCallback(callback);
}
