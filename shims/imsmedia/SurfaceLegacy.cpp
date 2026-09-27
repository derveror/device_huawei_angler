// SPDX-FileCopyrightText: 2026 The LineageOS Project
// SPDX-License-Identifier: Apache-2.0

#include <gui/Surface.h>

#include <new>

extern "C" void legacySurfaceConstructor(
        android::Surface* surface,
        const android::sp<android::IGraphicBufferProducer>& producer,
        bool controlledByApp)
        __asm__("_ZN7android7SurfaceC1ERKNS_2spINS_22IGraphicBufferProducerEEEb");

void legacySurfaceConstructor(
        android::Surface* surface,
        const android::sp<android::IGraphicBufferProducer>& producer,
        bool controlledByApp) {
    new (surface) android::Surface(
            producer, controlledByApp, android::sp<android::IBinder>{});
}
