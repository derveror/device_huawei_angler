#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

import hashlib
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
    'vendor/lib/libmmcamera2_imglib_modules.so',
    'vendor/lib/libmmcamera2_isp_modules.so',
    'vendor/lib/libmmcamera2_sensor_debug.so',
    'vendor/lib/libmmcamera2_sensor_modules.so',
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
    'remove unused DT_NEEDED libart-compiler.so; '
    'zero imported-symbol overlap'
)
ART_COMPILER_FIXUP_PATHS = {
    'vendor/lib/lib-imsrcscmclient.so',
    'vendor/lib64/lib-imsrcscmclient.so',
}
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

blob_fixups = {
    tuple(sorted(LIBSTDCXX_FIXUP_PATHS)): blob_fixup().replace_needed(
        'libstdc++.so',
        'libstdc++_vendor.so',
    ),
    tuple(sorted(QDUTILS_FIXUP_PATHS)): blob_fixup().remove_needed(
        'libqdutils.so',
    ),
    tuple(sorted(ART_COMPILER_FIXUP_PATHS)): blob_fixup().remove_needed(
        'libart-compiler.so',
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
        if file.dst in LIBSTDCXX_FIXUP_PATHS:
            fixup = LIBSTDCXX_FIXUP
        elif file.dst in QDUTILS_FIXUP_PATHS:
            fixup = QDUTILS_FIXUP
        elif file.dst in ART_COMPILER_FIXUP_PATHS:
            fixup = ART_COMPILER_FIXUP
        elif file.dst == ISP_MUTEX_FIXUP_PATH:
            fixup = ISP_MUTEX_FIXUP
        elif file.dst == Q3A64_COPY_RULE_PATH:
            fixup = Q3A64_COPY_RULE_PROVENANCE
        else:
            fixup = 'none'
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
        'explicit Qualcomm extraction path. Six closure files (two '
        'libaudcal and four camera libraries) are factory-only because '
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
