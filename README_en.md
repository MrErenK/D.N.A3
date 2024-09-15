#  **D.N.A** 

#### **Beta Version DNA3 Released**
#### **Introduction**

1. Full Name: Android General Firmware Unpack and Pack Assistant **Droid Normal Assistant** (D.N.A)

2. Supports common formats **_(*.zip, *.br, *.dat, *.dat.1~20, ext4/2 *.img, payload.bin, *.win000-004)_**, recognizes by extension, any name!

3. Supports unpacking Android 5.0+, supports unpacking Android 11 vendor.img
    - Test Package Mi10Pro: **_[miui_CMI_20.11.19_a7ff2a5b4e_11.0.zip](https://hugeota.d.miui.com/20.11.19/miui_CMI_20.11.19_a7ff2a5b4e_11.0.zip)_**

4. Supports packing Android [5.0+] **[Non-Dynamic Partition, Dynamic Partition]**, _due to lack of dynamic devices, flashing tests were not conducted_ ----2020.12.20
    - Android [5.0~8.1] uses **_[make_ext4fs]_** to pack img!!!
    - Android [9.0+] uses **_[mke2fs + e2fsdroid]_** to pack img!!!
    - Test Package Mi10Pro: **_[miui_CMI_20.12.10_a0bb9661ec_11.0.zip](https://hugeota.d.miui.com/20.12.10/miui_CMI_20.12.10_a0bb9661ec_11.0.zip)_** ----2020.12.20

5. Supports merging segmented *.dat.*, up to 20 segments (1~20, typically 15 segments in vivo ROMs, more segments slow down unpacking)
    - Test Package vivo Y9s: **_[PD1945_A_1.10.7-update-full_1589940104.zip](http://sysupwrdl.vivo.com.cn/upgrade/official/officialFiles/PD1945_A_1.10.7-update-full_1589940104.zip)_** ----2020.11.22

6. Supports unpacking payload.bin, automatically finds and unpacks all ext2/4 images after unpacking the bin, all in one step!!!
    - Test Package OnePlus8Pro: **_[OnePlus8ProHydrogen_15.Y.14_OTA_0140_all_2010200027_1bc1714063af44ff.zip](https://download.h2os.com/OnePlus8Pro/OBT/OnePlus8ProHydrogen_15.Y.14_OTA_0140_all_2010200027_1bc1714063af44ff.zip)_** ----2020.11.22

7. Supports unpacking TWRP backup files (excluding data), up to 4 files ( **_*.win000~004_** ) ----2020.11.24

8. Public beta for Linux version ----2020.11.30

9. Added plugin functionality, plugins located in the tool's relative path: DNA/Insides/Errors/submodules folder, public beta ----2020.12.21

10. Added MagiskBootKitchen (Android-Image-Kitchen) for unpacking and repacking [boot|exaid|recovery/etc].img ----2024.4.4

11. Supports unpacking some super.img (does not support dynamic AB dual system), latest Xiaomi 11 super.img not supported, public beta ----2021.01.09

12. Fixed inaccurate size recognition issue for some dynamic partitions! ----2021.01.09

13. Fixed packing error issue with **_[make_ext4fs]_**! ----2021.01.21

14. Added silent mode to the packing process (no prompts, automatically packs all packable content in the project directory) ----2021.01.21

#### **Software Architecture Supports**

1. Mobile Termux and above versions Arm64[aarch64] (natively supports TERMUX without a container!)

2. PC Win10 x86_64[x64]

3. Virtual or physical machine Ubuntu 20.04 and above versions x86_64[x64] recommended!!!

#### **Installation Tutorial [PC version tutorial starts from step 5] Each line below is a complete command**

1. Install the original [Termux.apk](https://search.f-droid.org/?q=termux&lang=zh_Hans) on your phone, run Termux and get storage permission
    - `termux-setup-storage`

###### Natively supports TERMUX without a container!

5. Enter the ubuntu/linux/termux system [**PC version tutorial starts here, mobile users continue below**] [Copy the command below and execute in the terminal]
    - `sudo apt update && sudo apt upgrade -y` [**Must execute, recent errors due to Tsinghua source issues, execute `mv -f /etc/apt/sources.list.bak /etc/apt/sources.list` and then re-execute this step, use a VPN if the network is slow**]
    - `sudo apt install git cpio aria2 brotli android-sdk-libsparse-utils openjdk-11-jre p7zip-full -y` [**Must execute, recommended to reinstall before using the new version**]

    - ~`sudo apt install zip unzip gawk sed curl wget -y`~ [Optional, not required]

6. Download this tool [Copy the command below and execute in the terminal]
    - `git clone https://github.com/ColdWindScholar/DNA3 -b feature --depth 1` [**Latest DNA3 public beta**]

7. After downloading, execute [Copy the command below and execute in the terminal]
    - `cd DNA && python3 dna.py`

8. At this point, you have started the tool, tutorial ends!
    - 1. In the future, to start the tool, just open Termux and enter [ `ubuntu` ] (if the tool exists)
    - 2. If you want to start the tool directly when opening Termux: In Termux (not in proot ubuntu, recommended to restart Termux and then execute) execute [ `echo -e "if [ -d ubuntu ] && [ $(command -v ubuntu) ]; then\n\tubuntu\nfi" >> .bashrc` ] then restart Termux to start the tool directly (if the tool exists)

#### **Usage Instructions**

1. Try not to use the system root function for all operations in Termux, PC requires root permission (sudo) and it is best not to run this tool under the root user login status to avoid permission issues after flashing the phone!

2. The tool needs to connect to the internet for version checking every time it starts, so it may be a bit slow; if used frequently, do not exit the tool

3. **About extracting zip on the phone**
    - Place the zip file in **/sdcard/Download** in internal storage, the tool will automatically search for it, if not found, place it in the tool directory

4. Tool directory in termux proot ubuntu on the phone: **/data/data/com.termux/files/home/ubuntu/root/DNA**

5. **Do not delete the [configs folder in the project directory], the files needed for packing are in this folder. If you want to modify the img size, you can open [project directory/configs/*_size.txt] and change the value to the size you want. The value must be in bytes. For dynamic partition packing exceeding the size, you can modify both [project directory/configs/*_size.txt] and [dynamic_partitions_op_list] such as [resize vendor ~2016763904~]. Since I don't have a dynamic partition device, I can't guarantee it will boot normally after packing!**

6. Due to phone performance, proot efficiency, and the tool's working method (e.g., automatically comparing and obtaining new files' fs_config before packing img each time, without immediate prompts), the tool may seem stuck, don't worry, be patient and wait for a moment

7. Try to delete files in [Termux or proot ubuntu] using [rm -rf file, folder] [**Do not use the system root function**]

8. **Do not run in folders with Chinese names, do not choose files with spaces for unpacking, project folders should not have spaces or other special characters!!!**

9. Update instructions: In proot ubuntu, delete the original DNA folder (remember to back up important files/plugins in the DNA folder), re-**`git clone https://github.com/ColdWindScholar/D.N.A3 --depth 1`**

10. **Dynamic partitions must be packed into the original official card flash package format [zip] (i.e., packed into .new.dat.br or .new.dat, and must use the dynamic_partitions_op_list in the project folder, compressed into a zip card flash package), single .img flashing is not allowed**

11. When using the tool on the phone, if you use **system ROOT** to operate on the project directory (e.g., **adding files, modifying files, etc.**), remember to give the operated files or folders **777** full permissions!!!

#### **Tool Preview**

![Image text](https://gitee.com/wenrou2554/dna_gitee/raw/master/views/2_view_x86_64.png)
![Image text](https://gitee.com/wenrou2554/dna_gitee/raw/master/views/3_view_x86_64.png)
![Image text](https://gitee.com/wenrou2554/dna_gitee/raw/master/views/4_view_x86_64.png)

#### **Feedback**

1. QQ Group 1: [MIO-KITCHEN Official Group 2](https://qm.qq.com/q/1UFWpnuiIY)
2. QQ Group 2: [DNA3](https://qm.qq.com/q/VE8gFAXZaq)

#### **Disclaimer**

1. This tool runs in the Termux proot environment, no root permission required, [**do not use the system root function in Termux**]!!!

2. This tool does not contain any illegal code such as [system destruction, data acquisition]!!!

3. **If data loss or damage occurs due to user operations on the project directory with root permissions, I am not responsible!!!**

#### [D.N.A3](https://github.com/ColdWindScholar/D.N.A3)
#### ColdWindScholar(3590361911@qq.com). All rights reserved.

