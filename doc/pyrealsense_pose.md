# pyrealsense.pose

> 本ドキュメントは [pyrealsense2 2.32.1 ドキュメントのpyrealsense.poseリファレンス](https://intelrealsense.github.io/librealsense/python_docs/_generated/pyrealsense2.pose.html) を翻訳したものです。

## class pyrealsense2.pose

### メソッド

#### __init__(self: pyrealsense2.pose) → None

### 属性

|属性名|説明|
|:--|:--|
|`acceleration`|加速度(X,Y,Z)、単位：m/sec^2|
|`angular_acceleration`|角加速度(X,Y,Z)、単位：ラジアン/sec^2|
|`angular_velocity`|角速度(X,Y,Z)、単位：ラジアン/sec|
|`mapper_confidence`|poseマップの信頼度(`0x0`:失敗、`0x1`:低、`0x2`:中、`0x3`:高)|
|`rotation`|四元数（初期位置に対する回転状態、(Qi, Qj, Qk, Ql)）|
|`tracker_confidence`|poseの信頼度(`0x0`:失敗、`0x1`:低、`0x2`:中、`0x3`:高)|
|`translation`|初期位置からの平行移動距離(X,Y,Z)、単位：m|
|`velocity`|速度(X,Y,Z)、単位：m/sec|

#### acceleration

加速度のX、Y、Z値、単位はメートル/秒^2。

#### angular_acceleration

角加速度のX、Y、Z値、単位はラジアン/秒^2。

> ラジアン：π＝180度

#### angular_velocity

角速度のX、Y、Z値、単位はラジアン/秒。

#### mapper_confidence

poseマップの信頼度（これまでのマッピングが正しいと認識しているかどうか）を数値で表したもの（`0x0`:失敗、`0x1`:低、`0x2`:中、`0x3`:高）

#### rotation

初期位置からの回転状態をあらわす四元数値のQi、Qj、Qk、Ql値。

#### tracker_confidence

poseの信頼度（これまでのトラッキング（位置情報）が正しいと認識しているかどうか）を数値で表したもの（`0x0`:失敗、`0x1`:低、`0x2`:中、`0x3`:高）

#### translation

初期位置からの平行移動したX、Y、Z値、単位はメートル。

#### velocity

速度のX、Y、Z値、単位はラジアン/秒。
