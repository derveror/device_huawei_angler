// SPDX-FileCopyrightText: 2026 The LineageOS Project
// SPDX-License-Identifier: Apache-2.0

#include <sensor/SensorManager.h>
#include <utils/String16.h>

android::sp<android::SensorEventQueue> legacyCreateEventQueue(
        android::SensorManager* manager,
        android::String8 packageName,
        int mode)
        __asm__("_ZN7android13SensorManager16createEventQueueENS_7String8Ei");

android::sp<android::SensorEventQueue> legacyCreateEventQueue(
        android::SensorManager* manager,
        android::String8 packageName,
        int mode) {
    return manager->createEventQueue(packageName, mode, android::String16(""));
}
