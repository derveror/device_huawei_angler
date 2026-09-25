#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from extract_utils.main import ExtractUtils, ExtractUtilsModule


# Keep this baseline fixup-free. A blob may be changed only after a recorded
# Android 15 loader/symbol failure identifies one exact compatibility patch.
module = ExtractUtilsModule(
    'angler',
    'huawei',
)


if __name__ == '__main__':
    ExtractUtils.device(module).run()
