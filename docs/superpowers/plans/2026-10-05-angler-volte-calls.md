# Angler VoLTE Calls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a source-built Android 15 IMS provider that registers Angler on AT&T VoLTE and passes real outgoing/incoming call tests without regressing the working RIL or LTE data path.

**Architecture:** A pinned Angler fork of PhhIms runs as the platform-signed privileged `me.phh.ims` service in its own process. Device and carrier RROs select it as the sole MMTEL provider; the incompatible Qualcomm IMS APK, daemons, init triggers, and SELinux policy are removed while the proven Angler QCRIL/netmgr/DPM stack remains unchanged.

**Tech Stack:** LineageOS 22.2 / Android 15, Soong, Kotlin/Java `ImsService`, SIP/IMS over the existing RIL IMS bearer, Python contract tests, Android RRO, vendor SELinux.

**Spec:** `device/huawei/angler/docs/superpowers/specs/2026-10-05-angler-volte-calls-design.md`

## Global Constraints

- Build only `lineage_angler-bp1a-userdebug`; use at most `-j6`.
- Keep kernel `3.10.108`; preserve fallback `3.10.73` unchanged.
- Do not modify or flash modem, radio, EFS, NV, calibration, or identity partitions.
- Do not wipe user data without separate permission.
- Preserve the working QCRIL, SMEM, DPM, netmgr, SIM, IMEI, baseband, and LTE-data fixes.
- Do not use Angler 18.1 as a donor and do not restore the OnePlus `org.codeaurora.ims` APK.
- Do not hard-code subscriber identifiers, credentials, P-CSCF addresses, or secrets; keep logs local and sanitized.
- Do not claim completion until outgoing and incoming calls with two-way audio pass again after a cold reboot.

## Review Focus

- A missing git submodule must not make a clean checkout unbuildable; Task 1 pins this with the PhhIms tree-contract test.
- Two overlays or two IMS packages must not compete for MMTEL; Task 2 asserts one provider, `me.phh.ims`.
- Removed Qualcomm daemons must not reappear through generated vendor makefiles; Task 3 tests both source lists and built images.
- An IMS failure must not restart `rild` or `com.android.phone`; Task 5 records and compares their PIDs during registration failure and recovery.
- Carrier rejection or absent provisioning must produce a classified, sanitized diagnostic instead of modem/EFS changes; Task 5 enforces that gate before any carrier-specific patch.

## File Map

- `packages/apps/PhhIms/Android.bp`: reproducible app-only Soong module without mandatory native submodules or a competing generic overlay.
- `packages/apps/PhhIms/app/src/main/AndroidManifest.xml`: privileged `ImsService` declaration and binding permission.
- `packages/apps/PhhIms/tools/test_android_tree_contract.py`: source-tree and privacy contract for a clean Lineage checkout.
- `.repo/local_manifests/angler.xml`: pins the current build workspace to the exact Angler PhhIms fork SHA.
- `device/huawei/angler/lineage.dependencies`: declares the branch dependency at `packages/apps/PhhIms` for the existing Angler manifest workflow.
- `device/huawei/angler/device.mk`: packages PhhIms and the Angler-specific IMS RROs.
- `device/huawei/angler/rro_overlays/Angler*ImsOverlay/**`: enables LTE VoLTE, disables VT/WFC, and selects `me.phh.ims`.
- `device/huawei/angler/configs/qti_whitelist.xml`: exempts `me.phh.ims`, not the removed Qualcomm package, from idle restrictions.
- `device/huawei/angler/rootdir/etc/init.angler.rc`: contains no Qualcomm IMS daemon lifecycle.
- `device/huawei/angler/sepolicy/vendor/{ims.te,file.te,file_contexts,property.te,property_contexts}`: removes policy used only by the discarded daemon stack.
- `device/huawei/angler/tests/{verify_ims_contract.py,verify_modem_compiled_policy.py}`: source and compiled-image regression gates.
- `device/huawei/angler/proprietary-files.txt`: excludes the obsolete IMS APK and four unused Qualcomm IMS executables.
- `vendor/huawei/angler/{Android.bp,angler-vendor.mk,BLOB_PROVENANCE.tsv}` and matching proprietary files: regenerated vendor output after the exclusions.

---

### Task 1: Create a reproducible Angler PhhIms source tree

**Files:**
- Create: `packages/apps/PhhIms/tools/test_android_tree_contract.py`
- Modify: `packages/apps/PhhIms/Android.bp`
- Modify: `packages/apps/PhhIms/app/src/main/AndroidManifest.xml`
- Delete: `packages/apps/PhhIms/.gitmodules`
- Delete: `packages/apps/PhhIms/app/jni/**`
- Delete: `packages/apps/PhhIms/overlay/**`

**Interfaces:**
- Consumes: Ultra-Legacy-Hippeastrum `ims` commit `a6ab624109e2ba01d6d9e59755114fd85c2b5f8e`.
- Produces: Soong module `PhhIms`, package `me.phh.ims`, service `me.phh.ims.PhhImsService`, fork branch `derveror/android_packages_apps_PhhIms:lineage-22.2-angler`.

- [ ] **Step 1: Write the failing clean-tree contract**

Create `tools/test_android_tree_contract.py` with tests asserting: module `PhhIms` is platform-signed, privileged, uses platform APIs, has no `jni_libs`, has no `required` generic overlay, declares the protected `android.telephony.ims.ImsService`, has no `.gitmodules`, defaults WebRTC AEC to disabled, and contains no captured subscriber identifiers or credentials in production sources/resources. Unit fixtures may use documented synthetic values.

- [ ] **Step 2: Run the contract and verify the donor fails**

Run: `python3 tools/test_android_tree_contract.py`

Expected: FAIL because native submodules and `PhhImsOverlay` are mandatory in the donor.

- [ ] **Step 3: Make the source tree reproducible**

Remove the two JNI module dependencies and generic overlay requirement from `Android.bp`; remove the unused submodule/native trees and generic overlay. Keep AEC disabled by `DEFAULT_DELAY_MS = 0`, retain the isolated app process and `BIND_IMS_SERVICE` manifest contract, and do not change SIP or carrier behavior pre-emptively.

- [ ] **Step 4: Run source tests**

Run: `python3 tools/test_android_tree_contract.py && ./gradlew test`

Expected: contract PASS and all JVM tests PASS.

- [ ] **Step 5: Commit the fork**

Run: `git add Android.bp app/src/main/AndroidManifest.xml tools/test_android_tree_contract.py .gitmodules app/jni overlay && git commit -m "build: make PhhIms reproducible for Angler"`

Expected: only PhhIms files are committed; push the commit to `lineage-22.2-angler` and record its SHA.

### Task 2: Select PhhIms as Angler's sole MMTEL provider

**Files:**
- Modify: `device/huawei/angler/tests/verify_ims_contract.py`
- Modify: `.repo/local_manifests/angler.xml`
- Modify: `device/huawei/angler/lineage.dependencies`
- Modify: `device/huawei/angler/device.mk`
- Modify: `device/huawei/angler/configs/qti_whitelist.xml`
- Modify: `device/huawei/angler/rro_overlays/AnglerTelephonyImsOverlay/res/values/config.xml`
- Modify: `device/huawei/angler/rro_overlays/AnglerCarrierConfigImsOverlay/res/xml/vendor.xml`

**Interfaces:**
- Consumes: `PhhIms` and its pinned fork SHA from Task 1.
- Produces: one MMTEL provider package name, `me.phh.ims`, used by product packaging, Telephony, CarrierConfig, and the power whitelist.
- Dependency tuple: repository `android_packages_apps_PhhIms`, path `packages/apps/PhhIms`, branch `lineage-22.2-angler`; local manifest remote `angler-github`, revision equal to the Task 1 SHA.

- [ ] **Step 1: Replace the stale Qualcomm contract with a failing PhhIms contract**

Update `verify_ims_contract.py` to assert the exact dependency repository/path/branch, `PRODUCT_PACKAGES += PhhIms`, the service manifest contract, and `me.phh.ims` in both RROs and the power whitelist. Assert LTE VoLTE is true, VT/WFC are false, and reject any `org.codeaurora.ims` selection or second packaged IMS APK. Add the fork to `angler.xml` with the exact Task 1 SHA because Lineage roomservice cannot create an arbitrary-owner GitHub project from `lineage.dependencies` alone.

- [ ] **Step 2: Run the source contract and verify failure**

Run: `python3 tests/verify_ims_contract.py`

Expected: FAIL because the dependency and overlays still select the removed Qualcomm package.

- [ ] **Step 3: Wire the pinned source module and overlays**

Add the branch dependency and exact-SHA local-manifest project, package `PhhIms` in the radio product group, change both package-selection resources and the power whitelist to `me.phh.ims`, and leave VoLTE-only capability values unchanged.

- [ ] **Step 4: Re-run device contracts**

Run: `python3 tests/verify_ims_contract.py && python3 tests/verify_build_target_contract.py`

Expected: both PASS and no forbidden target or subscriber-specific value appears in the diff.

- [ ] **Step 5: Commit the device integration**

Run: `git add lineage.dependencies device.mk configs/qti_whitelist.xml rro_overlays/AnglerTelephonyImsOverlay/res/values/config.xml rro_overlays/AnglerCarrierConfigImsOverlay/res/xml/vendor.xml tests/verify_ims_contract.py && git commit -m "telephony: integrate source-built PhhIms"`. Keep the workspace-only exact-SHA manifest change separate from repository commits.

### Task 3: Remove the failed Qualcomm IMS runtime without touching RIL

**Files:**
- Modify: `device/huawei/angler/tests/verify_ims_contract.py`
- Modify: `device/huawei/angler/tests/verify_modem_compiled_policy.py`
- Modify: `device/huawei/angler/rootdir/etc/init.angler.rc`
- Delete: `device/huawei/angler/sepolicy/vendor/ims.te`
- Modify: `device/huawei/angler/sepolicy/vendor/file.te`
- Modify: `device/huawei/angler/sepolicy/vendor/file_contexts`
- Modify: `device/huawei/angler/sepolicy/vendor/property.te`
- Modify: `device/huawei/angler/sepolicy/vendor/property_contexts`
- Modify: `device/huawei/angler/proprietary-files.txt`
- Regenerate: `vendor/huawei/angler/Android.bp`
- Regenerate: `vendor/huawei/angler/angler-vendor.mk`
- Modify: `vendor/huawei/angler/BLOB_PROVENANCE.tsv`
- Delete: the matching obsolete APK/executables from `vendor/huawei/angler/proprietary/**`

**Interfaces:**
- Consumes: the independent userspace provider from Task 2.
- Produces: a vendor image with unchanged QCRIL/netmgr/DPM components and no Qualcomm IMS APK, daemon, init trigger, socket label, or legacy IMS property namespace.

- [ ] **Step 1: Add failing absence checks**

Extend `verify_ims_contract.py` to reject `ims`, `ims_rtp_daemon`, `imscmservice`, `imsdatadaemon`, and `imsqmidaemon` in vendor packaging, init, file/property contexts, and proprietary source lists. Update `verify_modem_compiled_policy.py` to reject their installed paths while retaining every existing QCRIL, qmuxd, netmgrd, rild, DPM, audio, and RFSA assertion.

- [ ] **Step 2: Verify the old runtime is still detected**

Run: `python3 tests/verify_ims_contract.py`

Expected: FAIL and name the first remaining legacy IMS component.

- [ ] **Step 3: Remove only the obsolete IMS runtime**

Delete the two IMS services and triggers from `init.angler.rc`; remove their dedicated SELinux domain/socket/property definitions; delete the five proprietary-file entries; regenerate the vendor blueprint and makefile using the existing Angler extraction tooling. Keep the legacy IMS libraries because QCRIL dependency removal is not proven and they are not executable providers.

- [ ] **Step 4: Verify source policy and generated vendor output**

Run: `python3 tests/verify_ims_contract.py && git -C vendor/huawei/angler diff --check && git -C device/huawei/angler diff --check`

Expected: PASS; generated vendor packaging contains none of the five removed runtime modules.

- [ ] **Step 5: Commit explicit paths in each dirty repository**

Commit the device cleanup as `telephony: remove incompatible Qualcomm IMS runtime` and the generated vendor cleanup as `angler: drop obsolete Qualcomm IMS executables`, staging only the files listed in this task.

### Task 4: Build and inspect the minimal integration before OTA

**Files:**
- Build outputs: `out/target/product/angler/product.img`, `vendor.img`, and the incremental OTA zip.
- Diagnostic snapshot: `out/diagnostics/<timestamp>-phhims-preflash/`.

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: inspected images and a rollback snapshot; no device state change.

- [ ] **Step 1: Sync the pinned dependency and run all focused tests**

Run the normal dependency sync, then: `python3 packages/apps/PhhIms/tools/test_android_tree_contract.py && python3 device/huawei/angler/tests/verify_ims_contract.py && python3 device/huawei/angler/tests/verify_build_target_contract.py`.

Expected: all PASS and `packages/apps/PhhIms` is at the recorded fork SHA.

- [ ] **Step 2: Compile the app and overlays first**

Run after selecting `lineage_angler-bp1a-userdebug`: `m PhhIms AnglerFrameworkImsOverlay AnglerTelephonyImsOverlay AnglerCarrierConfigImsOverlay -j6`.

Expected: successful incremental build. Any Android 15 API correction stays inside the PhhIms fork, gets a focused JVM regression test, and is committed separately before continuing.

- [ ] **Step 3: Build affected images and compiled policy**

Run: `m productimage vendorimage-nodeps -j6`.

Expected: success; then `python3 device/huawei/angler/tests/verify_modem_compiled_policy.py` PASS.

- [ ] **Step 4: Inspect image contents**

Verify product contains one platform-signed `PhhIms.apk`; both installed RROs resolve to `me.phh.ims`; vendor contains none of the five removed Qualcomm IMS executables/APK; radio, qmuxd, netmgrd, DPM, and baseband files match the known-good image hashes.

- [ ] **Step 5: Build the incremental OTA and preserve rollback artifacts**

Build the OTA with `-j6`, reporting only each 10% milestone. Save the current known-good images, new image hashes, OTA hash, pinned source SHAs, and test results under the diagnostic snapshot; do not flash yet.

### Task 5: Prove IMS registration without destabilizing the phone stack

**Files:**
- Diagnostics: `out/diagnostics/<timestamp>-phhims-registration/`.
- Conditional fixes: only the PhhIms source file responsible for the observed registration stage, plus its matching `app/src/test/**` regression test.

**Interfaces:**
- Consumes: inspected OTA and rollback set from Task 4.
- Produces: a stable LTE MMTEL registration or an evidence-backed carrier/provisioning blocker without modifying modem/EFS/NV.

- [ ] **Step 1: Install without wiping data and capture the cold-boot baseline**

Sideload the OTA from recovery, boot normally, and record boot ID, baseband, masked IMEI/SIM state, LTE-data state, plus `rild` and `com.android.phone` PIDs. If normal boot fails, restore the Task 4 product/vendor rollback images without wiping data and collect recovery/ramoops evidence before changing code.

Expected: normal boot, baseband `angler-03.88`, SIM/IMEI/LTE data present, no boot loop.

- [ ] **Step 2: Verify service selection and isolation**

Confirm package `me.phh.ims` is platform/privileged, `ImsResolver` selects it for slot 0, no `org.codeaurora.ims` or Qualcomm IMS daemon runs, and both recorded phone-stack PIDs remain stable for at least two minutes.

Expected: the service is bound and a service failure, if any, does not restart RIL or Phone.

- [ ] **Step 3: Capture and classify registration**

Collect sanitized `ImsResolver`, `PhhImsService`, `PhhMmTelFeature`, `SipHandler`, Connectivity, TelephonyRegistry, and radio logs through IMS-network acquisition, P-CSCF discovery, AKA/IPsec, and SIP REGISTER.

Expected success marker: `IMS SIP registered, reporting registration tech LTE`, MMTEL voice capability enabled, and Telephony reports cellular IMS registration.

- [ ] **Step 4: Apply only an evidence-owned correction if registration fails**

Classify the first failure as service binding, IMS bearer, P-CSCF discovery, AKA/IPsec, SIP protocol, or carrier provisioning. For the first five classes, add a failing JVM test reproducing the exact sanitized input, implement the smallest correction in its owning PhhIms helper, rerun the complete Task 1 and Task 4 gates, and redeploy. For explicit carrier rejection/provisioning failure, stop code mutation and report the sanitized SIP status; modem/EFS/NV changes remain forbidden.

- [ ] **Step 5: Record the stable registration result**

Save sanitized evidence, image/source SHAs, and stable PID checks. Do not proceed to call testing without LTE MMTEL registration.

### Task 6: Verify real calls, audio, LTE stability, and cold boot

**Files:**
- Diagnostics: `out/diagnostics/<timestamp>-phhims-call-verification/`.
- Conditional audio fix: only the existing Angler audio route/HAL file proven by an established-call trace, with its existing audio regression test.

**Interfaces:**
- Consumes: stable LTE MMTEL registration from Task 5.
- Produces: real-device proof for outgoing/incoming VoLTE and a release-ready tree state.

- [ ] **Step 1: Arm sanitized call logging before user action**

Clear transient logs, start filtered Telephony/IMS/SIP/RTP/audio capture, and tell the user when to place the call. Never store the dialed number unmasked.

- [ ] **Step 2: Verify an outgoing call**

Expected: Telephony selects IMS rather than GSM/CS, SIP reaches the established state, the call remains active, hang-up completes cleanly, and sound works in both directions.

- [ ] **Step 3: Verify an incoming call**

Expected: incoming UI rings, answer establishes the call, sound works in both directions, and remote/local hang-up both cleanly release the dialog.

- [ ] **Step 4: Check regressions immediately after calls**

Verify unchanged baseband/IMEI/SIM, working LTE data, stable `rild`/`com.android.phone`, no ANR/reboot, and no recurring IMS or audio crash spam.

- [ ] **Step 5: Cold reboot and repeat the proof**

After a normal reboot, repeat Tasks 5.2–6.4 without runtime property tweaks. Expected: automatic LTE IMS registration and both call directions still pass.

- [ ] **Step 6: Final verification and commits**

Run all Angler contract tests, PhhIms JVM tests, compiled-policy checks, and an incremental OTA build. Commit any evidence-backed PhhIms/audio fixes separately; record final SHAs and sanitized results. Claim calls fixed only if every real-device criterion passes.
