# Raspbean Lite Buster 上へのlibrealsense(pyrealsense2)インストールする手順

## 前提

本ドキュメントの内容はすべて執筆時点(2020年2月27日）ベースで書いています。

### ハードウェア

* Raspberry Pi 4B/4GB
* 32GB SDカード

* Intel RealSense Tracking Camera T265 / USB3.0ケーブル
* USB3.0ケーブルおよび電源(となる母艦PC)
* インターネットへ接続可能なルータ

### ソフトウェア

* Raspbean Buster Lite (20200213)
* Intel RealSense SDK 2.0(build 2.32.1)
* Tera Term Ver4.98

## 手順

### SDカード書き込み

* 母艦PC上でSDカードをフォーマット
* Raspbean Buster Lite をダウンロード
* SDカードへRaspbean Buster Lite を書き込み
* SDカード上にルータ設定された wpa_supplicant.conf を書き込み
* SDカード上に空ファイル ssh を書き込み(初回からSSH接続可能に)

### OSセットアップ

* SDカードをRaspberry Piに刺す
* USB3.0ケーブルを使ってAC電源（母艦PCに）接続
* ping や spray を使ってRaspberry PiのIPアドレス特定
* ターミナルソフトを使って pi/raspberry でログイン
* `sudo vi /etc/dphys-swapfile` を実行し `CONF_SWAPSIZE=2048` 、`MAX_SWAPSIZE=2048` と書き換え保存
* `sudo /etc/init.d/dphys-swapfile restart swapon -s`
* `sudo raspi-config` を実行
* "7.Advanced Options" ＞ "A7 GL Driver" ＞ "Y" ＞ "G2 GL (Fake KMS)" を選択
* "7.Advanced Options" ＞ "A1 Expand Filesystem"
* 終了時rebootを選択し、リブート実行
* 再起動したら `sudo apt update && sudo apt upgrade -y` を実行

### 関連パッケージインストール

```bash
cd
sudo apt install -y libdrm-amdgpu1 libdrm-dev libdrm-exynos1 libdrm-freedreno1 libdrm-nouveau2 libdrm-omap1 libdrm-radeon1 libdrm-tegra0 libdrm2 libglu1-mesa libglu1-mesa-dev glusterfs-common libglu1-mesa libglu1-mesa-dev libglui-dev libglui2c2 mesa-utils mesa-utils-extra xorg-dev libgtk-3-dev libusb-1.0-0-dev cmake libprotobuf-dev libtbb-dev build-essential i2c-tools avahi-utils joystick libopenjp2-7-dev libtiff5-dev gfortran libatlas-base-dev libopenblas-dev libhdf5-serial-dev git ntp libilmbase-dev libopenexr-dev libgstreamer1.0-dev libjasper-dev libwebp-dev libatlas-base-dev libavcodec-dev libavformat-dev libswscale-dev libqtgui4 libqt4-test
sudo apt install -y python3 python3-dev python3-opencv python3-pip python3-protobuf python3-opengl python3-virtualenv python3-numpy python3-picamera python3-pandas python3-rpi.gpio
sudo -H pip3 install pyopengl
sudo -H pip3 install pyopengl_accelerate
```

### librealsense/pyrealsense2 インストール

```bash
cd ~/ && mkdir -p projects && cd projects
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
sudo cp config/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
sudo reboot
vi ~/.bashrc を実行し以下の２行を追加、保存する
echo "export LD_LIBRARY_PATH=/usr/local/lib:\$LD_LIBRARY_PATH"  >> ~/.bashrc
echo "export PYTHONPATH=\$PYTHONPATH:/usr/local/lib"  >> ~/.bashrc
source ~/.bashrc
cd ~/projects/librealsense
mkdir build && cd build
cmake .. -DBUILD_EXAMPLES=true -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)
make -j4
sudo make install
sudo ldconfig
```

### 動作確認

```bash
lsusb ※接続前の状態を確認（接続後との比較用）
dmesg |grep -i usb ※接続前の状態を確認（接続後との比較用）
```

* Raspberry Pi 4B の青い USB3.0 コネクタにT265を接続し、電源を接続して起動

```bash
lsusb
```

> ※私の環境の場合、接続後以下のメッセージが追加
> `Bus 001 Device 003: ID 03e7:2150 Intel Myriad VPU [Movidius Neural Compute Stick]`

```bash
dmesg |grep -i usb
```

> ※私の環境の場合、接続後以下のメッセージが追加
>
> ```bash
> [  133.058275] usb 1-1.2: new high-speed USB device number 3 using xhci_hcd
> [  133.189229] usb 1-1.2: New USB device found, idVendor=03e7, idProduct=21XXX, bcdDevice= 0.01
> [  133.189245] usb 1-1.2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
> [  133.189258] usb 1-1.2: Product: Movidius MA2X5X
> [  133.189271] usb 1-1.2: Manufacturer: Movidius Ltd.
> [  133.189283] usb 1-1.2: SerialNumber: 03e72XXX```

```bash
cd ~/projects/librealsense/wrapper/python/example
python3 t265_example.py
```

エラーがないことを確認。

### Donkeycar実行環境のインストール

```bash
cd ~/
python3 -m virtualenv -p python3 env --system-site-packages
echo "source ~/env/bin/activate" >> ~/.bashrc
source ~/.bashrc
cd ~/projects
git clone https://github.com/autorope/donkeycar
cd donkeycar
git checkout master
git pull
pip install -e .[pi]
pip install tensorflow==1.14.0
sudo shutdown -h now
```

### 補足

[Raspberry Pi3へインストールする公式ドキュメント](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md) は、Raspbean streach 前提であり、このままでは buster ではインストールできない。

* 一部ライブラリのデバッグモードパッケージが存在しない
* `udevadm trigger` に `sudo` がない
* `cmake`、`protobuf`、TBB、OpenCVはbusterパッケージリポジトリのもので動作する
* `make -j1`だと遅い（自分の環境(4B)では`make -j4`でもコンパイルできた）が、3B+の場合は`-j1`以外で最後まで一気にコンパイル成功したことはない
