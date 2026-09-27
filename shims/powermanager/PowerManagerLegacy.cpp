// SPDX-FileCopyrightText: 2026 The LineageOS Project
// SPDX-License-Identifier: Apache-2.0

#include <android/os/IPowerManager.h>
#include <binder/IBinder.h>
#include <utils/StrongPointer.h>

android::sp<android::os::IPowerManager>
legacyPowerManagerAsInterface(const android::sp<android::IBinder>& binder)
        __asm__("_ZN7android13IPowerManager11asInterfaceERKNS_2spINS_7IBinderEEE");

android::sp<android::os::IPowerManager> legacyPowerManagerAsInterface(
        const android::sp<android::IBinder>& binder) {
    return android::os::IPowerManager::asInterface(binder);
}
