#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
# Copyright (C) 2024 The MIO-KITCHEN-SOURCE Project
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html#license-text
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from re import escape
from typing import Generator

fix_permission = {
    "system/app/*/.apk": "u:object_r:system_file:s0",
    "data-app/.apk": "u:object_r:system_file:s0",
    "android.hardware.wifi": "u:object_r:hal_wifi_default_exec:s0",
    "bin/idmap": "u:object_r:idmap_exec:s0",
    "bin/fsck": "u:object_r:fsck_exec:s0",
    "bin/e2fsck": "u:object_r:fsck_exec:s0",
    "bin/logcat": "u:object_r:logcat_exec:s0",
    "system/bin": "u:object_r:system_file:s0",
    "/system/bin/init": "u:object_r:init_exec:s0",
    r"/lost\+found": "u:object_r:rootfs:s0"
}


def scan_context(file) -> dict:  # Read the context file and return a dictionary
    context = {}
    with open(file, "r", encoding='utf-8') as file_:
        for i in file_.readlines():
            if not i.strip():
                print('[W] data is empty!')
                continue
            filepath, *other = i.strip().split()
            filepath = filepath.replace(r'\@', '@')
            context[filepath] = other
            if len(other) > 1:
                print(f"[Warn] {i[0]} has too much data. Skip.")
                del context[filepath]
    return context

def scan_dir(folder) -> Generator[str, None, None]:  # Read the unpacked directory and return a list
    part_name = os.path.basename(folder)
    allfiles = ['/', '/lost+found', f'/{part_name}/lost+found', f'/{part_name}', f'/{part_name}/']
    for root, dirs, files in os.walk(folder, topdown=True):
        for dir_ in dirs:
            yield os.path.join(root, dir_).replace(folder, '/' + part_name).replace('\\', '/')
        for file in files:
            yield os.path.join(root, file).replace(folder, '/' + part_name).replace('\\', '/')
        yield from allfiles


def str_to_selinux(string: str):
    return escape(string).replace('\\-', '-')


def context_patch(fs_file, dir_path) -> tuple:  # Receive two dictionaries and compare
    new_fs = {}
    # Define already patched to avoid duplicate patches
    r_new_fs = {}
    add_new = 0
    print(f"ContextPatcher: the Original File Has {len(fs_file.keys()):d} entries")
    # Define default SeLinux label
    permission_d = ['u:object_r:system_file:s0']
    for i in scan_dir(os.path.abspath(dir_path)):
        # Replace non-printable characters with *
        if not i.isprintable():
            tmp = ''
            for c in i:
                tmp += c if c.isprintable() else '*'
            i = tmp
        if ' ' in i:
            i = i.replace(' ', '*')
        i = str_to_selinux(i)
        if fs_file.get(i):
            # If it exists, use the default
            new_fs[i] = fs_file[i]
        else:
            permission = None
            if r_new_fs.get(i):
                continue
            # Ensure i is not empty
            if i:
                # Search for defined permissions
                for f in fix_permission.keys():
                    if f in i:
                        permission = [fix_permission[f]]
                if not permission:
                    permission = permission_d
            if " " in permission[0]:
                permission = [permission[0].replace(' ', '')]
            print(f"ADD [{i} {permission}]")
            add_new += 1
            r_new_fs[i] = permission
            new_fs[i] = permission
    return new_fs, add_new


def main(dir_path, fs_config) -> None:
    new_fs, add_new = context_patch(scan_context(os.path.abspath(fs_config)), dir_path)
    with open(fs_config, "w+", encoding='utf-8', newline='\n') as f:
        f.writelines([i + " " + " ".join(new_fs[i]) + "\n" for i in sorted(new_fs.keys())])
    print(f'ContextPatcher: Add {add_new:d} entries')
