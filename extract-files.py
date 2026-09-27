#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

import hashlib
import struct
from pathlib import Path

from extract_utils.file import File
from extract_utils.fixups_blob import blob_fixup
from extract_utils.main import ExtractUtils, ExtractUtilsModule
from extract_utils.postprocess import PostprocessCtx


HUAWEI_LICENSE_PROVENANCE = (
    'Huawei official driver vendor.img; OPM7.181205.001'
)
QUALCOMM_LICENSE_PROVENANCE = (
    'Qualcomm official driver explicit path; OPM7.181205.001'
)
FACTORY_ONLY_LICENSE_PROVENANCE = (
    'Google factory image exact; differs from Huawei driver package; '
    'local closure only; OPM7.181205.001'
)
QUALCOMM_EXPLICIT_PATHS = {
    'system/bin/ssr_setup',
    'system/bin/subsystem_ramdump',
    'system/etc/permissions/cneapiclient.xml',
    'system/etc/permissions/qcrilhook.xml',
}
FACTORY_ONLY_CLOSURE_PATHS = {
    'vendor/lib/libaudcal.so',
    'vendor/lib/libmmcamera_imglib.so',
    'vendor/lib/libmmcamera2_imglib_modules.so',
    'vendor/lib/libmmcamera2_isp_modules.so',
    'vendor/lib/libmmcamera2_sensor_debug.so',
    'vendor/lib/libmmcamera2_sensor_modules.so',
    'vendor/lib/libmmcamera2_stats_modules.so',
    'vendor/lib64/libaudcal.so',
}
LIBSTDCXX_FIXUP = (
    'replace DT_NEEDED libstdc++.so with source-built libstdc++_vendor.so'
)
LIBSTDCXX_FIXUP_PATHS = {
    'vendor/lib/libgoog_eis_armeabi-v7a.so',
    'vendor/lib/libgoog_rownr.so',
    'vendor/lib/libmmcamera_faceproc.so',
}
QDUTILS_FIXUP = (
    'remove unused DT_NEEDED libqdutils.so; zero imported-symbol overlap'
)
QDUTILS_FIXUP_PATHS = {
    'vendor/lib/libmm-qdcm.so',
    'vendor/lib64/libmm-qdcm.so',
}
ART_COMPILER_FIXUP = (
    'remove unused DT_NEEDED libart-compiler.so and libart.so; '
    'zero imported-symbol overlap'
)
ART_COMPILER_FIXUP_PATHS = {
    'vendor/lib/lib-imsrcscmclient.so',
    'vendor/lib64/lib-imsrcscmclient.so',
}
LEGACY_LIBLOG_FIXUP_PATHS = {
    'vendor/bin/cnd',
    'vendor/bin/imsdatadaemon',
    'vendor/bin/imsqmidaemon',
    'vendor/bin/loc_launcher',
    'vendor/bin/port-bridge',
    'vendor/lib/lib-imsSDP.so',
    'vendor/lib/lib-imsdpl.so',
    'vendor/lib/lib-imss.so',
    'vendor/lib/lib-rtpdaemoninterface.so',
    'vendor/lib/libQSEEComAPI.so',
    'vendor/lib/libcne.so',
    'vendor/lib/libcneapiclient.so',
    'vendor/lib/libmmcamera2_frame_algorithm.so',
    'vendor/lib/libmmcamera2_is.so',
    'vendor/lib/libmmcamera2_q3a_core.so',
    'vendor/lib/libmmcamera2_stats_algorithm.so',
    'vendor/lib/libmmcamera_cac2_lib.so',
    'vendor/lib/libmmcamera_pdaf.so',
    'vendor/lib/libmmcamera_pdafcamif.so',
    'vendor/lib/libmmcamera_tintless_bg_pca_algo.so',
    'vendor/lib64/lib-imsSDP.so',
    'vendor/lib64/lib-imsdpl.so',
    'vendor/lib64/lib-imss.so',
    'vendor/lib64/lib-rtpdaemoninterface.so',
    'vendor/lib64/libQSEEComAPI.so',
    'vendor/lib64/lib_fpc_tac_shared.so',
    'vendor/lib64/libcne.so',
    'vendor/lib64/libcneapiclient.so',
    'vendor/lib64/libizat_core.so',
    'vendor/lib64/liblbs_core.so',
    'vendor/lib64/liblowi_client.so',
    'vendor/lib64/liblowi_wifihal.so',
    'vendor/lib64/libmmcamera2_q3a_core.so',
    'vendor/lib64/libmmcamera2_stats_algorithm.so',
    'vendor/lib64/libquipc_os_api.so',
}
LEGACY_LIBLOG_FIXUP = (
    'add direct liblog DT_NEEDED for legacy Android log imports'
)
SCHED_POLICY_FIXUP_PATHS = {
    'vendor/lib/libvoice-svc.so',
    'vendor/lib64/libvoice-svc.so',
}
SCHED_POLICY_FIXUP = (
    'add direct libprocessgroup DT_NEEDED for set_sched_policy'
)
CUTILS_STRING_SHIM_FIXUP_PATHS = {
    'vendor/bin/ATFWD-daemon',
    'vendor/lib/libcne.so',
    'vendor/lib64/libcne.so',
}
CUTILS_STRING_SHIM_FIXUP = (
    'add source-built libcutils_shim DT_NEEDED for legacy UTF conversion'
)
POWER_MANAGER_SHIM_FIXUP_PATHS = {
    'vendor/lib/libmm-abl.so',
    'vendor/lib64/libmm-abl.so',
}
POWER_MANAGER_SHIM_FIXUP = (
    'add forwarding power-manager namespace shim for legacy asInterface'
)
SURFACE_SHIM_FIXUP_PATHS = {
    'vendor/lib/libimsmedia_jni.so',
    'vendor/lib64/libimsmedia_jni.so',
}
SURFACE_SHIM_FIXUP = (
    'add forwarding Surface constructor shim with null control handle'
)
ISP_MUTEX_FIXUP_PATH = 'vendor/lib/libmmcamera2_isp_modules.so'
ISP_MUTEX_FIXUP = (
    'move CBNZ before mutex destruction for Android P FORTIFY; '
    'PixelBoot provenance 1b95fec2e5f4e5c2432e5885d5ef705e82ecb245'
)
Q3A64_COPY_RULE_PATH = 'vendor/lib64/libmmcamera2_q3a_core.so'
Q3A64_COPY_RULE_PROVENANCE = (
    'exact copy rule: stock has no 64-bit libmmcamera2_is provider; '
    'runtime camera daemon is 32-bit'
)
LIBC_PRIVATE_VERSION_FIXUP_PATHS = {
    'vendor/lib/hw/gatekeeper.msm8994.so',
    'vendor/lib/lib-dplmedia.so',
    'vendor/lib/lib-ims-rcscmjni.so',
    'vendor/lib/lib-imsSDP.so',
    'vendor/lib/lib-imsdpl.so',
    'vendor/lib/lib-imsqimf.so',
    'vendor/lib/lib-imsrcs.so',
    'vendor/lib/lib-imsrcscm.so',
    'vendor/lib/lib-imsrcscmclient.so',
    'vendor/lib/lib-imsrcscmservice.so',
    'vendor/lib/lib-imss.so',
    'vendor/lib/lib-imsxml.so',
    'vendor/lib/lib-rcsimssjni.so',
    'vendor/lib/lib-rcsjni.so',
    'vendor/lib/lib-rtpcommon.so',
    'vendor/lib/lib-rtpcore.so',
    'vendor/lib/lib-rtpdaemoninterface.so',
    'vendor/lib/lib-rtpsl.so',
    'vendor/lib/libQSEEComAPI.so',
    'vendor/lib/libadm.so',
    'vendor/lib/libadpcmdec.so',
    'vendor/lib/libadsprpc.so',
    'vendor/lib/libcneapiclient.so',
    'vendor/lib/libconfigdb.so',
    'vendor/lib/libdrmfs.so',
    'vendor/lib/libdrmtime.so',
    'vendor/lib/libdsi_netctrl.so',
    'vendor/lib/libdsutils.so',
    'vendor/lib/liblistensoundmodel2.so',
    'vendor/lib/libmdsprpc.so',
    'vendor/lib/libmm-abl.so',
    'vendor/lib/libmm-disp-apis.so',
    'vendor/lib/libmm-qdcm.so',
    'vendor/lib/libmmcamera2_frame_algorithm.so',
    'vendor/lib/libmmcamera2_is.so',
    'vendor/lib/libmmcamera2_stats_algorithm.so',
    'vendor/lib/libmmcamera_pdaf.so',
    'vendor/lib/libmmcamera_pdafcamif.so',
    'vendor/lib/libmmcamera_tintless_algo.so',
    'vendor/lib/libmmcamera_tintless_bg_pca_algo.so',
    'vendor/lib/libnetmgr.so',
    'vendor/lib/libqdi.so',
    'vendor/lib/librpmb.so',
    'vendor/lib/libscale.so',
    'vendor/lib/libssd.so',
    'vendor/lib/libtzdrmgenprov.so',
}
LIBC_PRIVATE_VERSION_FIXUP = (
    'retarget audited legacy ARM EABI imports from LIBC_PRIVATE to the '
    'ABI-identical LIBC_N aliases exported by current Bionic'
)


def _elf_hash(value: bytes):
    result = 0
    for byte in value:
        result = (result << 4) + byte
        high = result & 0xF0000000
        if high:
            result ^= high >> 24
        result &= ~high
    return result


def retarget_libc_private_version(
    _ctx,
    _file,
    file_path,
    *_args,
    **_kwargs,
):
    data = bytearray(Path(file_path).read_bytes())
    if data[:6] != b'\x7fELF\x01\x01':
        raise ValueError(f'{file_path}: expected a little-endian ELF32 file')

    section_offset = struct.unpack_from('<I', data, 32)[0]
    section_entry_size = struct.unpack_from('<H', data, 46)[0]
    section_count = struct.unpack_from('<H', data, 48)[0]
    if section_entry_size < 40:
        raise ValueError(f'{file_path}: invalid ELF32 section entry size')

    sections = [
        struct.unpack_from(
            '<IIIIIIIIII',
            data,
            section_offset + index * section_entry_size,
        )
        for index in range(section_count)
    ]
    verneed_sections = [section for section in sections if section[1] == 0x6FFFFFFE]
    if len(verneed_sections) != 1:
        raise ValueError(f'{file_path}: expected exactly one GNU verneed section')

    verneed = verneed_sections[0]
    dynstr_index = verneed[6]
    if dynstr_index >= len(sections) or sections[dynstr_index][1] != 3:
        raise ValueError(f'{file_path}: GNU verneed does not link to a string table')
    dynstr = sections[dynstr_index]
    dynstr_offset, dynstr_size = dynstr[4], dynstr[5]

    old_name = b'LIBC_PRIVATE'
    new_name = b'LIBC_N'
    old_hash = _elf_hash(old_name)
    new_hash = _elf_hash(new_name)
    patched = 0
    relative = 0
    while relative < verneed[5]:
        current = verneed[4] + relative
        _, aux_count, _, aux_relative, next_relative = struct.unpack_from(
            '<HHIII', data, current
        )
        aux = current + aux_relative
        for _ in range(aux_count):
            version_hash, _, _, name_relative, next_aux = struct.unpack_from(
                '<IHHII', data, aux
            )
            name_start = dynstr_offset + name_relative
            name_end = data.index(0, name_start, dynstr_offset + dynstr_size)
            if bytes(data[name_start:name_end]) == old_name:
                if version_hash != old_hash:
                    raise ValueError(f'{file_path}: LIBC_PRIVATE hash mismatch')
                padded_name = new_name + bytes(len(old_name) - len(new_name))
                data[name_start:name_end] = padded_name
                struct.pack_into('<I', data, aux, new_hash)
                patched += 1
            if next_aux == 0:
                break
            aux += next_aux
        if next_relative == 0:
            break
        relative += next_relative

    if patched != 1:
        raise ValueError(
            f'{file_path}: expected one LIBC_PRIVATE version need, found {patched}'
        )
    Path(file_path).write_bytes(data)


def _libc_private_fixup():
    return blob_fixup().call(
        retarget_libc_private_version,
        need_tmp_dir=False,
    )


def _legacy_liblog_fixup(path):
    fixup = (
        _libc_private_fixup()
        if path in LIBC_PRIVATE_VERSION_FIXUP_PATHS
        else blob_fixup()
    )
    fixup.add_needed('liblog.so')
    if path in CUTILS_STRING_SHIM_FIXUP_PATHS:
        fixup.add_needed('libcutils_shim.so')
    return fixup


blob_fixups = {
    tuple(sorted(LIBSTDCXX_FIXUP_PATHS)): blob_fixup().replace_needed(
        'libstdc++.so',
        'libstdc++_vendor.so',
    ),
    'vendor/lib64/libmm-qdcm.so': blob_fixup().remove_needed('libqdutils.so'),
    'vendor/lib/libmm-qdcm.so': (
        blob_fixup().remove_needed('libqdutils.so').call(
            retarget_libc_private_version,
            need_tmp_dir=False,
        )
    ),
    'vendor/lib64/lib-imsrcscmclient.so': (
        blob_fixup()
        .remove_needed('libart-compiler.so')
        .remove_needed('libart.so')
    ),
    'vendor/lib/lib-imsrcscmclient.so': (
        blob_fixup()
        .remove_needed('libart-compiler.so')
        .remove_needed('libart.so')
        .call(retarget_libc_private_version, need_tmp_dir=False)
    ),
    **{
        path: _legacy_liblog_fixup(path)
        for path in sorted(LEGACY_LIBLOG_FIXUP_PATHS)
    },
    tuple(
        sorted(CUTILS_STRING_SHIM_FIXUP_PATHS - LEGACY_LIBLOG_FIXUP_PATHS)
    ): blob_fixup().add_needed('libcutils_shim.so'),
    'vendor/lib64/libmm-abl.so': (
        blob_fixup().add_needed('libpowermanager_legacy_shim.so')
    ),
    'vendor/lib/libmm-abl.so': (
        _libc_private_fixup().add_needed('libpowermanager_legacy_shim.so')
    ),
    tuple(sorted(SURFACE_SHIM_FIXUP_PATHS)): (
        blob_fixup().add_needed('libsurface_legacy_shim.so')
    ),
    tuple(sorted(SCHED_POLICY_FIXUP_PATHS)): (
        blob_fixup().add_needed('libprocessgroup.so')
    ),
    ISP_MUTEX_FIXUP_PATH: blob_fixup().sig_replace(
        (
            '06 9A 02 F5 46 3E 0E F5 EA 70 20 F0 5C FC 06 99 '
            '01 F5 46 30 00 F5 EC 70 20 F0 55 FC 06 9B 03 F5 '
            '46 3C 0C F5 EE 70 20 F0 4E FC 06 9E 06 F5 46 32 '
            '02 F5 E8 70 20 F0 4F FC 0C B9'
        ),
        (
            'EC B9 06 9A 02 F5 46 3E 0E F5 EA 70 20 F0 5B FC '
            '06 99 01 F5 46 30 00 F5 EC 70 20 F0 54 FC 06 9B '
            '03 F5 46 3C 0C F5 EE 70 20 F0 4D FC 06 9E 06 F5 '
            '46 32 02 F5 E8 70 20 F0 4E FC'
        ),
    ),
    tuple(
        sorted(
            LIBC_PRIVATE_VERSION_FIXUP_PATHS
            - {
                'vendor/lib/libmm-qdcm.so',
                'vendor/lib/lib-imsrcscmclient.so',
                'vendor/lib/libmm-abl.so',
            }
            - LEGACY_LIBLOG_FIXUP_PATHS
        )
    ): _libc_private_fixup(),
}


def _iter_proprietary_files(path: Path):
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if line and not line.startswith('#'):
            yield File(line)


def _classify_blob(blob: Path, destination: str):
    header = blob.read_bytes()[:20]
    if header.startswith(b'\x7fELF'):
        elf_class = {1: 'ELF32', 2: 'ELF64'}.get(header[4], 'unknown')
        byte_order = 'little' if header[5] == 1 else 'big'
        machine_id = int.from_bytes(header[18:20], byte_order)
        machine = {
            40: 'ARM',
            94: 'Tensilica Xtensa',
            164: 'Qualcomm Hexagon',
            183: 'AArch64',
        }.get(machine_id, f'EM_{machine_id}')
        kind = 'firmware-ELF' if '/firmware/' in f'/{destination}' else 'ELF'
        return kind, elf_class, machine

    if '/firmware/' in f'/{destination}':
        return 'firmware', '', ''
    if blob.suffix in {'.cfg', '.conf', '.sql', '.txt', '.xml'}:
        return 'configuration', '', ''
    return 'data', '', ''


def write_blob_metadata(_ctx: PostprocessCtx):
    device_path = Path(module.device_path)
    vendor_path = Path(module.vendor_path)
    proprietary_path = vendor_path / 'proprietary'
    rows = []

    for file in _iter_proprietary_files(device_path / 'proprietary-files.txt'):
        blob = proprietary_path / file.dst
        kind, elf_class, machine = _classify_blob(blob, file.dst)
        if file.src in QUALCOMM_EXPLICIT_PATHS:
            license_provenance = QUALCOMM_LICENSE_PROVENANCE
        elif file.src in FACTORY_ONLY_CLOSURE_PATHS:
            license_provenance = FACTORY_ONLY_LICENSE_PROVENANCE
        else:
            license_provenance = HUAWEI_LICENSE_PROVENANCE
        fixups = []
        if file.dst in LIBSTDCXX_FIXUP_PATHS:
            fixups.append(LIBSTDCXX_FIXUP)
        if file.dst in QDUTILS_FIXUP_PATHS:
            fixups.append(QDUTILS_FIXUP)
        if file.dst in ART_COMPILER_FIXUP_PATHS:
            fixups.append(ART_COMPILER_FIXUP)
        if file.dst in LEGACY_LIBLOG_FIXUP_PATHS:
            fixups.append(LEGACY_LIBLOG_FIXUP)
        if file.dst in SCHED_POLICY_FIXUP_PATHS:
            fixups.append(SCHED_POLICY_FIXUP)
        if file.dst in CUTILS_STRING_SHIM_FIXUP_PATHS:
            fixups.append(CUTILS_STRING_SHIM_FIXUP)
        if file.dst in POWER_MANAGER_SHIM_FIXUP_PATHS:
            fixups.append(POWER_MANAGER_SHIM_FIXUP)
        if file.dst in SURFACE_SHIM_FIXUP_PATHS:
            fixups.append(SURFACE_SHIM_FIXUP)
        if file.dst == ISP_MUTEX_FIXUP_PATH:
            fixups.append(ISP_MUTEX_FIXUP)
        if file.dst == Q3A64_COPY_RULE_PATH:
            fixups.append(Q3A64_COPY_RULE_PROVENANCE)
        if file.dst in LIBC_PRIVATE_VERSION_FIXUP_PATHS:
            fixups.append(LIBC_PRIVATE_VERSION_FIXUP)
        fixup = '; '.join(fixups) if fixups else 'none'
        rows.append(
            (
                file.src,
                file.dst,
                hashlib.sha256(blob.read_bytes()).hexdigest(),
                str(blob.stat().st_size),
                kind,
                elf_class,
                machine,
                license_provenance,
                fixup,
            )
        )

    rows.sort(key=lambda row: (row[1], row[0]))
    fields = (
        'source_path',
        'destination',
        'sha256',
        'bytes',
        'kind',
        'elf_class',
        'machine',
        'license_provenance',
        'fixup',
    )
    lines = ['\t'.join(fields), *('\t'.join(row) for row in rows)]
    (vendor_path / 'BLOB_PROVENANCE.tsv').write_text('\n'.join(lines) + '\n')

    (vendor_path / 'README.md').write_text(
        '# Proprietary files for Google Nexus 6P (angler)\n\n'
        'This tree is generated from official Google OPM7.181205.001 inputs. '
        'Every admitted source file is byte-identical to the factory image. '
        'Most are covered by the official Huawei vendor-image package or an '
        'explicit Qualcomm extraction path. Eight closure files (two '
        'libaudcal and six camera libraries) are factory-only because '
        'the same paths in the Huawei package contain different bytes; their '
        'provenance is recorded explicitly. The ISP module is regenerated '
        'from the exact stock input with a scoped Android P mutex/FORTIFY '
        'instruction fix whose upstream provenance is pinned in the metadata.\n\n'
        'Huawei archive SHA-256: '
        '`2eb9a77de059739d33c7fad07e34034f03a93d70eea39460bb0d9278e5763053`.\n\n'
        'Qualcomm archive SHA-256: '
        '`78222d6c627020d8312477f647253b37569882ebdfe527207f39074dc05fc6a1`.\n\n'
        '`BLOB_PROVENANCE.tsv` records source/destination paths, SHA-256, '
        'size, file type, ELF identity, license provenance, and any scoped '
        'output fixup. License '
        'acceptance for local extraction does not authorize unrestricted '
        'public redistribution; do not push proprietary bytes until that '
        'policy is reviewed separately.\n'
    )


# Keep this baseline fixup-free. A blob may be changed only after a recorded
# Android 15 loader/symbol failure identifies one exact compatibility patch.
module = ExtractUtilsModule(
    'angler',
    'huawei',
    blob_fixups=blob_fixups,
    namespace_imports=['vendor/qcom/opensource/dataservices'],
)
module.add_postprocess_fn(write_blob_metadata)


if __name__ == '__main__':
    ExtractUtils.device(module).run()
