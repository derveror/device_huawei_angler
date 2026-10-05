#
# Copyright (C) 2015 The Android Open Source Project
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

LOCAL_PATH := device/huawei/angler

# Device-specific framework and application resources.
PRODUCT_PACKAGE_OVERLAYS += $(LOCAL_PATH)/overlay

# Export the source-built rmnet provider to Kati so proprietary data-service
# binaries retain their declared ELF dependency during Make conversion.
PRODUCT_SOONG_NAMESPACES += \
    hardware/qcom/audio \
    hardware/qcom-caf/msm8994/media \
    hardware/qcom/display \
    vendor/qcom/opensource/dataservices

# Resource selection follows the physical 1440 x 2560 display.
PRODUCT_AAPT_CONFIG := normal
PRODUCT_AAPT_PREF_CONFIG := 560dpi
PRODUCT_AAPT_PREBUILT_DPI := xxxhdpi xxhdpi xhdpi hdpi
PRODUCT_CHARACTERISTICS := nosdcard

PRODUCT_SYSTEM_PROPERTIES += \
    debug.hwui.use_buffer_age=false \
    debug.renderengine.backend=gles \
    debug.sf.predict_hwc_composition_strategy=0 \
    ro.hardware.egl=adreno \
    ro.surface_flinger.max_frame_buffer_acquired_buffers=3

PRODUCT_VENDOR_PROPERTIES += \
    debug.mdpcomp.logs=0 \
    persist.vendor.hwc.mdpcomp.enable=true \
    persist.vendor.hwc.mdpcomp.maxpermixer=4 \
    persist.vendor.hwc.ptor.enable=true \
    persist.vendor.hwc.pubypass=true \
    persist.vendor.mdpcomp.4k2kSplit=1 \
    persist.vendor.mdpcomp_perfhint=50 \
    persist.vendor.metadata_dynfps.disable=true \
    vendor.rild.libpath=/vendor/lib64/libril-qc-qmi-1.so \
    ro.hardware.sensors=nanohub

# Stock Angler QCRIL settings. The Android 15 rild bridge consumes the vendor
# library path above and exposes the legacy RIL through HIDL radio 1.1.
PRODUCT_SYSTEM_PROPERTIES += \
    persist.data.dpm.enable=true \
    persist.data.mode=concurrent \
    persist.radio.always_send_plmn=true \
    persist.radio.apm_sim_not_pwdn=1 \
    persist.radio.custom_ecc=1 \
    persist.radio.data_con_rprt=true \
    persist.radio.data_no_toggle=1 \
    persist.radio.mode_pref_nv10=1 \
    persist.radio.snapshot_enabled=1 \
    persist.radio.snapshot_timer=2 \
    ro.com.android.prov_mobiledata=false \
    ro.telephony.call_ring.multiple=0 \
    ro.telephony.default_cdma_sub=0 \
    ro.telephony.default_network=10 \
    ro.use_data_netmgrd=true \
    telephony.lteOnCdmaDevice=1

# The stock 3.10 kernel has no eBPF syscall or bpffs. Connectivity uses this
# legacy opt-out to avoid treating missing BPF maps as a fatal boot error.
PRODUCT_SYSTEM_PROPERTIES += \
    ro.kernel.ebpf.supported=false

$(call inherit-product, frameworks/native/build/phone-xhdpi-2048-dalvik-heap.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/non_ab_device.mk)

# Root and recovery configuration
PRODUCT_PACKAGES += \
    fstab.angler \
    init.angler.diag.rc \
    init.angler.rc \
    init.angler.root.rc \
    init.angler.sensorhub.rc \
    init.angler.usb.rc \
    init.recovery.angler.rc \
    ueventd.angler.rc

# UsbService is started only when the product declares USB host or accessory.
PRODUCT_COPY_FILES += \
    frameworks/native/data/etc/android.hardware.camera.flash-autofocus.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.flash-autofocus.xml \
    frameworks/native/data/etc/android.hardware.camera.front.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.front.xml \
    frameworks/native/data/etc/android.hardware.camera.full.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.full.xml \
    frameworks/native/data/etc/android.hardware.camera.raw.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.camera.raw.xml \
    frameworks/native/data/etc/android.hardware.sensor.barometer.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.barometer.xml \
    frameworks/native/data/etc/android.hardware.sensor.gyroscope.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.gyroscope.xml \
    frameworks/native/data/etc/android.hardware.sensor.hifi_sensors.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.hifi_sensors.xml \
    frameworks/native/data/etc/android.hardware.sensor.light.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.light.xml \
    frameworks/native/data/etc/android.hardware.sensor.proximity.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.proximity.xml \
    frameworks/native/data/etc/android.hardware.sensor.stepcounter.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.stepcounter.xml \
    frameworks/native/data/etc/android.hardware.sensor.stepdetector.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.sensor.stepdetector.xml \
    frameworks/native/data/etc/android.hardware.telephony.cdma.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.telephony.cdma.xml \
    frameworks/native/data/etc/android.hardware.telephony.gsm.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.telephony.gsm.xml \
    frameworks/native/data/etc/android.hardware.telephony.ims.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.telephony.ims.xml \
    frameworks/native/data/etc/android.hardware.usb.accessory.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.usb.accessory.xml \
    frameworks/native/data/etc/android.hardware.usb.host.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.usb.host.xml \
    frameworks/native/data/etc/android.hardware.wifi.direct.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.wifi.direct.xml \
    frameworks/native/data/etc/android.hardware.wifi.passpoint.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.wifi.passpoint.xml \
    frameworks/native/data/etc/android.hardware.wifi.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.wifi.xml

# Keymaster is required before file-encrypted /data can be initialized.
PRODUCT_PACKAGES += \
    android.hardware.keymaster@3.0-impl \
    android.hardware.keymaster@3.0-service

# Radio. Stock QCRIL is exposed by rild as HIDL 1.1. The Lineage legacy
# adapter promotes it to HIDL 1.4, the oldest version accepted by Android 15.
PRODUCT_PACKAGES += \
    AnglerCarrierConfigImsOverlay \
    AnglerFrameworkImsOverlay \
    AnglerTelephonyImsOverlay \
    PhhIms \
    android.hardware.radio@1.4-service.legacy \
    android.hardware.radio.config@1.1-service.angler \
    angler_netmgr_config_compat \
    libangler_peripheral_refbase_compat \
    librmnetctl

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/qti_whitelist.xml:system/etc/sysconfig/qti_whitelist.xml \
    $(LOCAL_PATH)/rootdir/bin/init.mcfg.sh:$(TARGET_COPY_OUT_VENDOR)/bin/init.mcfg.sh \
    $(LOCAL_PATH)/rootdir/bin/init.radio.sh:$(TARGET_COPY_OUT_VENDOR)/bin/init.radio.sh

# Camera. Angler's Google-published HAL is 32-bit; the matching HIDL service
# bridges it to the current framework and also exposes torch control.
PRODUCT_PACKAGES += \
    android.hardware.camera.provider@2.4-impl \
    android.hardware.camera.provider@2.4-service \
    camera.msm8994

# Legacy Qualcomm codecs and persistent input surfaces used by CameraX video.
PRODUCT_PACKAGES += \
    android.hardware.media.omx@1.0-service

# Sensors. The rear camera consumes the physical gyroscope through the stock
# Google sensor-synchronization module, so the nanohub HAL is required before
# camera streaming can start.
PRODUCT_PACKAGES += \
    android.frameworks.sensorservice@1.0.vendor \
    android.hardware.sensors@1.0-impl \
    libsensorndkbridge \
    nanoapp_cmd \
    sensors.nanohub

# Vibrator. Use the callback-free HIDL bridge for Angler's timed-output HAL.
# The generic AIDL legacy bridge advertises ON_CALLBACK but never completes it,
# leaving every short haptic active until the framework timeout.
PRODUCT_PACKAGES += \
    android.hardware.vibrator@1.0-impl \
    android.hardware.vibrator@1.0-service

# Health
PRODUCT_PACKAGES += \
    android.hardware.health@2.1-impl-angler \
    android.hardware.health@2.1-impl-angler.recovery \
    android.hardware.health@2.1-service

# Audio
PRODUCT_SYSTEM_PROPERTIES += \
    persist.audio.product.identify=angler

PRODUCT_PACKAGES += \
    android.hardware.audio@7.1-impl \
    android.hardware.audio.effect@7.0-impl \
    android.hardware.audio.service \
    audio.primary.msm8994 \
    audio.r_submix.default \
    audio.usb.default \
    libaudio-resampler \
    libqcompostprocbundle \
    libqcomvisualizer \
    libqcomvoiceprocessing

# Display
PRODUCT_PACKAGES += \
    android.hardware.graphics.allocator@2.0-impl \
    android.hardware.graphics.allocator@2.0-service \
    android.hardware.graphics.composer@2.1-service \
    android.hardware.graphics.mapper@2.0-impl-2.1 \
    android.hardware.memtrack@1.0-impl \
    android.hardware.memtrack@1.0-service \
    copybit.msm8994 \
    disable_configstore \
    gralloc.msm8994 \
    hwcomposer.msm8994 \
    memtrack.msm8994 \
    liboverlay \
    libtinyxml

# Angler's panel and notification LEDs are exposed through sysfs. The
# device-specific HIDL service converts framework light states to those nodes.
PRODUCT_PACKAGES += \
    android.hardware.light@2.0-service.angler

# This is a legacy non-Treble device, but its HAL inventory is complete.
# Enforcing the manifest makes HIDL reject unavailable newer HAL versions
# immediately instead of waiting one second for every version it probes.
PRODUCT_ENFORCE_VINTF_MANIFEST_OVERRIDE := true

# Audio configuration. The msm8994 audio HAL runs in a vendor domain and
# resolves device configuration from /vendor/etc before /system/etc.
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/audio/aanc_tuning_mixer.txt:$(TARGET_COPY_OUT_VENDOR)/etc/aanc_tuning_mixer.txt \
    $(LOCAL_PATH)/audio/audio_effects.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_effects.xml \
    $(LOCAL_PATH)/audio/audio_output_policy.conf:$(TARGET_COPY_OUT_VENDOR)/etc/audio_output_policy.conf \
    $(LOCAL_PATH)/audio/audio_platform_info.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_platform_info.xml \
    $(LOCAL_PATH)/audio/audio_platform_info_i2s.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_platform_info_i2s.xml \
    $(LOCAL_PATH)/audio/audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_policy_configuration.xml \
    $(LOCAL_PATH)/audio/audio_policy_volumes_drc.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_policy_volumes_drc.xml \
    $(LOCAL_PATH)/audio/mixer_paths.xml:$(TARGET_COPY_OUT_VENDOR)/etc/mixer_paths.xml \
    $(LOCAL_PATH)/audio/sound_trigger_mixer_paths.xml:$(TARGET_COPY_OUT_VENDOR)/etc/sound_trigger_mixer_paths.xml \
    $(LOCAL_PATH)/audio/sound_trigger_platform_info.xml:$(TARGET_COPY_OUT_VENDOR)/etc/sound_trigger_platform_info.xml \
    frameworks/av/services/audiopolicy/config/a2dp_in_audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/a2dp_in_audio_policy_configuration.xml \
    frameworks/av/services/audiopolicy/config/bluetooth_audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/bluetooth_audio_policy_configuration.xml \
    frameworks/av/services/audiopolicy/config/default_volume_tables.xml:$(TARGET_COPY_OUT_VENDOR)/etc/default_volume_tables.xml \
    frameworks/av/services/audiopolicy/config/r_submix_audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/r_submix_audio_policy_configuration.xml \
    frameworks/av/services/audiopolicy/config/usb_audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/usb_audio_policy_configuration.xml

# Media codec and camera profile configuration. Codec XML belongs to vendor:
# the legacy OMX service runs in the mediacodec vendor domain and cannot read
# an Angler-specific configuration mislabeled as a system file.
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/media/media_codecs.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs.xml \
    $(LOCAL_PATH)/media/media_codecs_performance.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_performance.xml \
    $(LOCAL_PATH)/media/media_profiles.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/media_profiles.xml \
    frameworks/av/media/libstagefright/data/media_codecs_google_audio.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_google_audio.xml \
    frameworks/av/media/libstagefright/data/media_codecs_google_telephony.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_google_telephony.xml \
    frameworks/av/media/libstagefright/data/media_codecs_google_video.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_google_video.xml

# Qualcomm msm8994 video codec implementation used by the legacy OMX HAL.
PRODUCT_PACKAGES += \
    libc2dcolorconvert \
    libminijail_32 \
    libOmxCore \
    libOmxVdec \
    libOmxVenc \
    libstagefrighthw \
    libstagefright_softomx_plugin.vendor

# Device input maps
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/keylayout/gpio-keys.kl:$(TARGET_COPY_OUT_SYSTEM)/usr/keylayout/gpio-keys.kl \
    $(LOCAL_PATH)/keylayout/qpnp_pon.kl:$(TARGET_COPY_OUT_SYSTEM)/usr/keylayout/qpnp_pon.kl \
    $(LOCAL_PATH)/keylayout/synaptics_dsx.idc:$(TARGET_COPY_OUT_SYSTEM)/usr/idc/synaptics_dsx.idc \
    $(LOCAL_PATH)/keylayout/uinput-fpc.idc:$(TARGET_COPY_OUT_SYSTEM)/usr/idc/uinput-fpc.idc \
    $(LOCAL_PATH)/keylayout/uinput-fpc.kl:$(TARGET_COPY_OUT_SYSTEM)/usr/keylayout/uinput-fpc.kl

# Stock device-daemon configuration
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/gps.conf:$(TARGET_COPY_OUT_SYSTEM)/etc/gps.conf \
    $(LOCAL_PATH)/configs/msm_irqbalance.conf:$(TARGET_COPY_OUT_VENDOR)/etc/msm_irqbalance.conf \
    $(LOCAL_PATH)/configs/sec_config:$(TARGET_COPY_OUT_VENDOR)/etc/sec_config \
    $(LOCAL_PATH)/configs/thermal-engine-angler.conf:$(TARGET_COPY_OUT_SYSTEM)/etc/thermal-engine.conf

# BCM4358 firmware calibration and supplicant overlays
PRODUCT_PACKAGES += \
    android.hardware.wifi-service \
    hostapd \
    libwpa_client \
    wificond \
    wpa_supplicant \
    wpa_supplicant.conf

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/wifi/bcmdhd-high.cal:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/bcmdhd-high.cal \
    $(LOCAL_PATH)/wifi/bcmdhd-low.cal:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/bcmdhd-low.cal \
    $(LOCAL_PATH)/wifi/bcmdhd-pme.cal:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/bcmdhd-pme.cal \
    $(LOCAL_PATH)/wifi/bcmdhd.cal:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/bcmdhd.cal \
    $(LOCAL_PATH)/wifi/filter_ie:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/filter_ie \
    $(LOCAL_PATH)/configs/p2p_supplicant_overlay.conf:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/p2p_supplicant_overlay.conf \
    $(LOCAL_PATH)/configs/wpa_supplicant_overlay.conf:$(TARGET_COPY_OUT_VENDOR)/etc/wifi/wpa_supplicant_overlay.conf

$(call inherit-product-if-exists, hardware/broadcom/wlan/bcmdhd/firmware/bcm4358/device-bcm.mk)

# Proprietary modules are generated in Stage 5 and remain optional here so the
# open product contract can be parsed independently.
$(call inherit-product-if-exists, vendor/huawei/angler/angler-vendor.mk)
