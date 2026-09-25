#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

import hashlib
from pathlib import Path

from extract_utils.file import File
from extract_utils.main import ExtractUtils, ExtractUtilsModule
from extract_utils.postprocess import PostprocessCtx


HUAWEI_LICENSE_PROVENANCE = (
    'Huawei official driver vendor.img; OPM7.181205.001'
)
QUALCOMM_LICENSE_PROVENANCE = (
    'Qualcomm official driver explicit path; OPM7.181205.001'
)
QUALCOMM_EXPLICIT_PATHS = {
    'system/bin/ssr_setup',
    'system/bin/subsystem_ramdump',
    'system/etc/permissions/cneapiclient.xml',
    'system/etc/permissions/qcrilhook.xml',
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
        license_provenance = (
            QUALCOMM_LICENSE_PROVENANCE
            if file.src in QUALCOMM_EXPLICIT_PATHS
            else HUAWEI_LICENSE_PROVENANCE
        )
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
    )
    lines = ['\t'.join(fields), *('\t'.join(row) for row in rows)]
    (vendor_path / 'BLOB_PROVENANCE.tsv').write_text('\n'.join(lines) + '\n')

    (vendor_path / 'README.md').write_text(
        '# Proprietary files for Google Nexus 6P (angler)\n\n'
        'This tree is generated from official Google OPM7.181205.001 inputs. '
        'Every admitted file is byte-identical to the factory image and is '
        'covered by either the official Huawei vendor-image package or an '
        'explicit Qualcomm extraction path.\n\n'
        'Huawei archive SHA-256: '
        '`2eb9a77de059739d33c7fad07e34034f03a93d70eea39460bb0d9278e5763053`.\n\n'
        'Qualcomm archive SHA-256: '
        '`78222d6c627020d8312477f647253b37569882ebdfe527207f39074dc05fc6a1`.\n\n'
        '`BLOB_PROVENANCE.tsv` records source/destination paths, SHA-256, '
        'size, file type, ELF identity, and license provenance. License '
        'acceptance for local extraction does not authorize unrestricted '
        'public redistribution; do not push proprietary bytes until that '
        'policy is reviewed separately.\n'
    )


# Keep this baseline fixup-free. A blob may be changed only after a recorded
# Android 15 loader/symbol failure identifies one exact compatibility patch.
module = ExtractUtilsModule(
    'angler',
    'huawei',
)
module.add_postprocess_fn(write_blob_metadata)


if __name__ == '__main__':
    ExtractUtils.device(module).run()
