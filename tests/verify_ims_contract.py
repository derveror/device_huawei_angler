#!/usr/bin/env python3

import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


top = Path(__file__).resolve().parents[4]
device = top / "device/huawei/angler"
phhims = top / "packages/apps/PhhIms"
local_manifest = top / ".repo/local_manifests/angler.xml"
phhims_revision = "d1f5f96dae976fe5fa1ec1a271a5fdf1597cce3e"


def text(path: Path) -> str:
    if not path.is_file():
        sys.exit(f"missing {path.relative_to(top)}")
    return path.read_text()


def require(path: Path, pattern: str, description: str) -> None:
    if not re.search(pattern, text(path), re.MULTILINE):
        sys.exit(description)


dependencies = json.loads(text(device / "lineage.dependencies"))
expected_dependency = {
    "repository": "android_packages_apps_PhhIms",
    "target_path": "packages/apps/PhhIms",
    "branch": "lineage-22.2-angler",
}
if expected_dependency not in dependencies:
    sys.exit("lineage.dependencies does not pin the Angler PhhIms fork branch")

manifest = ET.parse(local_manifest).getroot()
projects = [
    project
    for project in manifest.findall("project")
    if project.attrib.get("path") == "packages/apps/PhhIms"
]
if len(projects) != 1:
    sys.exit("the local manifest must contain exactly one PhhIms project")
if projects[0].attrib != {
    "name": "android_packages_apps_PhhIms",
    "path": "packages/apps/PhhIms",
    "remote": "angler-github",
    "revision": phhims_revision,
}:
    sys.exit("the local manifest does not pin the exact audited PhhIms revision")

app_manifest = ET.parse(phhims / "app/src/main/AndroidManifest.xml").getroot()
android_ns = "{http://schemas.android.com/apk/res/android}"
if app_manifest.attrib.get("package") != "me.phh.ims":
    sys.exit("the source-built IMS package must be me.phh.ims")
services = app_manifest.findall("application/service")
if len(services) != 1:
    sys.exit("PhhIms must expose exactly one IMS service")
service = services[0]
if service.attrib.get(f"{android_ns}name") != "me.phh.ims.PhhImsService":
    sys.exit("PhhIms does not expose the audited service implementation")
if service.attrib.get(f"{android_ns}permission") != "android.permission.BIND_IMS_SERVICE":
    sys.exit("PhhIms does not protect the service with BIND_IMS_SERVICE")
actions = {
    action.attrib.get(f"{android_ns}name")
    for action in service.findall("intent-filter/action")
}
if actions != {"android.telephony.ims.ImsService"}:
    sys.exit("PhhIms does not expose the platform IMS service action")


device_mk = device / "device.mk"
require(
    device_mk,
    r"^\s*frameworks/native/data/etc/android\.hardware\.telephony\.ims\.xml:"
    r"\$\(TARGET_COPY_OUT_VENDOR\)/etc/permissions/android\.hardware\.telephony\.ims\.xml",
    "the product does not declare IMS telephony hardware support",
)
if re.search(r"^\s*ims(?:\s*\\)?$", text(device_mk), re.MULTILINE):
    sys.exit("the product must not select a second packaged IMS APK")
require(
    device_mk,
    r"^\s*PhhIms(?:\s*\\)?$",
    "the source-built PhhIms module is not packaged",
)
require(
    device_mk,
    r"qti_whitelist\.xml:system/etc/sysconfig/qti_whitelist\.xml",
    "the IMS service is not exempted from idle power restrictions",
)

static_base_overlay_path = (
    device / "overlay/frameworks/base/core/res/res/values/config.xml"
)
static_base_overlay = text(static_base_overlay_path)
for resource in (
    "config_device_volte_available",
    "config_device_vt_available",
    "config_device_wfc_ims_available",
):
    if resource in static_base_overlay:
        sys.exit(
            f"{resource} must use an independent RRO to avoid rebuilding framework-res"
        )

rro_bp = device / "rro_overlays/Android.bp"
for module in (
    "AnglerFrameworkImsOverlay",
    "AnglerTelephonyImsOverlay",
    "AnglerCarrierConfigImsOverlay",
):
    require(
        device_mk,
        rf"^\s*{module}(?:\s*\\)?$",
        f"{module} is not packaged",
    )
    require(
        rro_bp,
        rf'(?s)runtime_resource_overlay\s*\{{.*?name:\s*"{module}".*?'
        rf'certificate:\s*"platform".*?product_specific:\s*true',
        f"{module} is not an independent platform-signed product RRO",
    )

framework_manifest = ET.parse(
    device / "rro_overlays/AnglerFrameworkImsOverlay/AndroidManifest.xml"
).getroot()
framework_overlay = framework_manifest.find("overlay")
if framework_overlay is None or framework_overlay.attrib.get(
    f"{android_ns}targetPackage"
) != "android":
    sys.exit("the framework IMS RRO does not target android")

base_overlay = ET.parse(
    device / "rro_overlays/AnglerFrameworkImsOverlay/res/values/config.xml"
).getroot()
base_bools = {
    item.attrib["name"]: (item.text or "").strip()
    for item in base_overlay.findall("bool")
}
if base_bools.get("config_device_volte_available") != "true":
    sys.exit("the device overlay does not expose Angler VoLTE capability")

telephony_manifest = ET.parse(
    device / "rro_overlays/AnglerTelephonyImsOverlay/AndroidManifest.xml"
).getroot()
telephony_manifest_overlay = telephony_manifest.find("overlay")
if telephony_manifest_overlay is None or telephony_manifest_overlay.attrib.get(
    f"{android_ns}targetPackage"
) != "com.android.phone":
    sys.exit("the Telephony IMS RRO does not target com.android.phone")

telephony_overlay = ET.parse(
    device / "rro_overlays/AnglerTelephonyImsOverlay/res/values/config.xml"
).getroot()
telephony_strings = {
    item.attrib["name"]: (item.text or "").strip()
    for item in telephony_overlay.findall("string")
}
if telephony_strings.get("config_ims_mmtel_package") != "me.phh.ims":
    sys.exit("Telephony is not bound to the source-built PhhIms service")

carrier_manifest = ET.parse(
    device / "rro_overlays/AnglerCarrierConfigImsOverlay/AndroidManifest.xml"
).getroot()
carrier_manifest_overlay = carrier_manifest.find("overlay")
if carrier_manifest_overlay is None or carrier_manifest_overlay.attrib.get(
    f"{android_ns}targetPackage"
) != "com.android.carrierconfig":
    sys.exit("the CarrierConfig IMS RRO does not target com.android.carrierconfig")

carrier_overlay = ET.parse(
    device / "rro_overlays/AnglerCarrierConfigImsOverlay/res/xml/vendor.xml"
).getroot()
carrier = next(
    (
        item
        for item in carrier_overlay.findall("carrier_config")
        if item.attrib.get("mcc") == "310" and item.attrib.get("mnc") == "410"
    ),
    None,
)
if carrier is None or not any(
    item.attrib.get("name") == "carrier_volte_available_bool"
    and item.attrib.get("value") == "true"
    for item in carrier.findall("boolean")
):
    sys.exit("the tested carrier profile does not enable VoLTE")
carrier_values = {
    item.attrib.get("name"): item.attrib.get("value")
    for item in carrier
    if item.tag in {"boolean", "string"}
}
if carrier_values.get("config_ims_mmtel_package_override_string") != "me.phh.ims":
    sys.exit("the tested carrier profile does not select PhhIms MMTEL")
if carrier_values.get("carrier_vt_available_bool") != "false":
    sys.exit("video telephony must remain disabled during bring-up")
if carrier_values.get("carrier_wfc_ims_available_bool") != "false":
    sys.exit("Wi-Fi calling must remain disabled during bring-up")

whitelist = ET.parse(device / "configs/qti_whitelist.xml").getroot()
power_save_packages = {
    item.attrib.get("package") for item in whitelist.findall("allow-in-power-save")
}
if power_save_packages != {"me.phh.ims"}:
    sys.exit("the power whitelist must contain only the selected PhhIms package")

selected_files = (
    device_mk,
    device / "configs/qti_whitelist.xml",
    device / "rro_overlays/AnglerTelephonyImsOverlay/res/values/config.xml",
    device / "rro_overlays/AnglerCarrierConfigImsOverlay/res/xml/vendor.xml",
)
if any("org.codeaurora.ims" in text(path) for path in selected_files):
    sys.exit("a product configuration still selects the Qualcomm IMS package")

print("Angler selects source-built PhhIms as its sole MMTEL provider")
