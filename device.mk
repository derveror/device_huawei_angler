#
# Copyright (C) 2015 The Android Open Source Project
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

LOCAL_PATH := device/huawei/angler

# Resource selection follows the physical 1440 x 2560 display.
PRODUCT_AAPT_CONFIG := normal
PRODUCT_AAPT_PREF_CONFIG := 560dpi
PRODUCT_AAPT_PREBUILT_DPI := xxxhdpi xxhdpi xhdpi hdpi
PRODUCT_CHARACTERISTICS := nosdcard

$(call inherit-product, frameworks/native/build/phone-xhdpi-2048-dalvik-heap.mk)

# Proprietary modules are generated in Stage 5 and remain optional here so the
# open product contract can be parsed independently.
$(call inherit-product-if-exists, vendor/huawei/angler/angler-vendor.mk)
