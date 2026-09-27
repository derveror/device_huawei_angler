// SPDX-FileCopyrightText: 2026 The LineageOS Project
// SPDX-License-Identifier: Apache-2.0

#include <math.h>

float legacyRenderScriptFloor(float value) __asm__("_Z9SC_floorff");

float legacyRenderScriptFloor(float value) {
    static float (*volatile currentFloor)(float) = floorf;
    return currentFloor(value);
}
