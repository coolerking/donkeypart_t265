# Intel RealSense Tracking Camera T265 全センサデータ取得可能なDonkeyパーツクラス

Intel RealSense Tracking Camera T265 から取得可能な全センサデータをDonkeycarで使用できるパーツクラスを提供する。

* Intel RealSense Tracking Camera T265の座標系などの概要は [こちら](./doc/t265.md) を参照のこと。
* [Raspberry Pi 3B/Streach 前提のlibrealsense/pyrealsense2 インストール手順](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md) は [公式リポジトリ](https://github.com/IntelRealSense/librealsense/) 上にドキュメント有り。
* [Raspbean Lite Buster 上へのlibrealsense(pyrealsense2)インストールする手順](./doc/install_librealsense_on_buster.md) は [こちら](./doc/install_librealsense_on_buster.md) 。

## 取得可能データ

以下、`FullDataReader` クラスの`run()`および`run_threaded()` メソッドの戻り値である。

|ラベル|タイプ|説明|
|:------|:------|:---|
|`pos_x`|`float`|位置情報X軸（単位：メートル）|
|`pos_y`|`float`|位置情報Y軸（単位：メートル）|
|`pos_z`|`float`|位置情報Z軸（単位：メートル）|
|`vel_x`|`float`|速度X軸（単位：メートル/秒）|
|`vel_y`|`float`|速度Y軸（単位：メートル/秒）|
|`vel_z`|`float`|速度Z軸（単位：メートル/秒）|
|`e_vel_x`|`float`|角速度X軸、gyr_xに相当（単位：ラジアン/秒）|
|`e_vel_y`|`float`|角速度Y軸、gyr_yに相当（単位：ラジアン/秒）|
|`e_vel_z`|`float`|角速度Z軸、gyr_zに相当（単位：ラジアン/秒）|
|`acc_x`|`float`|加速度X軸（単位：メートル/秒^2）|
|`acc_y`|`float`|加速度Y軸（単位：メートル/秒^2）|
|`acc_z`|`float`|加速度Z軸（単位：メートル/秒^2）|
|`e_acc_x`|`float`|角加速度X軸（単位：ラジアン/秒^2）|
|`e_acc_y`|`float`|角加速度Y軸（単位：ラジアン/秒^2）|
|`e_acc_z`|`float`|角加速度Z軸（単位：ラジアン/秒^2）|
|`rot_i`|`float`|四元数(Qi)|
|`rot_j`|`float`|四元数(Qj)|
|`rot_k`|`float`|四元数(Qk)|
|`rot_l`|`float`|四元数(Ql)|
|`ang_x`|`float`|オイラー角X軸(ロール)（単位：ラジアン）|
|`ang_y`|`float`|オイラー角Y軸(ピッチ)（単位：ラジアン）|
|`ang_z`|`float`|オイラー角Z軸(ヨー)（単位：ラジアン）|
|`posemap_conf`|`float`|poseマップ信頼度：0x0-失敗、0x1-低、0x2-中、0x3-高|
|`pose_conf`|`float`|pose信頼度：0x0-失敗、0x1-低、0x2-中、0x3-高|
|`left_image_array`|`image_array`|左カメライメージ(nd.array型、`(800,848)` 形式)|
|`right_image_array`|`image_array`|右カメライメージ(`nd.array`型、`(800,848)` 形式)|

> Donkeycarのデフォルトカメライメージは`(120, 160, 3)形式であるため、そのまま学習モデルの入力層に渡すことはできないことに注意。

pythonラッパpyrealsense2で取得可能なセンサ情報は [こちら](./doc/pyrealsense_pose.md) を参照のこと。

## インストール

librealsense/pyrealsense2 が有効なDonkeycar v3.1.1 実行環境を構築し、次のコマンドを実行する。

> Raspberry Pi4B/busterへlibrealsense/pyrealsense2をインストールする手順は [こちら](./doc/install_librealsense_on_buster.md) を参照のこと。

```bash
cd ~/projects
git clone https://github.com/coolerking/donkeypart_t265
cd donkeypart_t265
git checkout master
git pull
pip install -e .
```

## 利用例

インストール後manage.py drive()を変更してパーツクラスをVehicleフレームワークへaddする。以下のコードはパーツクラス追加例である。

```python
    :
    from realsense2 import T265
    V.add(T265(image_output=True, debug=False),
        outputs=['rs/pos_x', 'rs/pos_y', 'rs/pos_z',
            'rs/vel_x', 'rs/vel_y', 'rs/vel_z',
            'rs/gyr_x', 'rs/gyr_y', 'rs/gyr_z',
            'rs/acc_x', 'rs/acc_y', 'rs/acc_z',
            'rs/gyr_ax', 'rs/gyr_ay', 'rs/gyr_az',
            'rs/rot_i', 'rs/rot_j', 'rs/rot_k', 'rs/rot_l',
            'rs/posemap_conf', 'rs/pose_conf',
            'rs/roll', 'rs/pitch', 'rs/yaw',
            'rs/left_image_array', 'rs/right_image_array'],
        threaded=True) # 別スレッド実行
    :
```

> 上記のように別スレッドで実行する場合、最初の数回はセンサからのデータが取得できていない状態の場合がる。その際は値がすべて `0`（イメージは`None`）となることに注意。

## ライセンス

本リポジトリのリソースはすべて [MITライセンス](./LICENSE) 準拠とする。
