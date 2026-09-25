#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

import runpy
import sys
from pathlib import Path


if __name__ == '__main__':
    # Current extract-utils generates Android.bp/Make metadata itself. Keep a
    # dedicated entry point for the documented workflow without duplicating
    # module configuration.
    sys.argv.insert(1, '-m')
    runpy.run_path(Path(__file__).with_name('extract-files.py'), run_name='__main__')
