# -*- coding: utf-8 -*-
"""
Donkeycar用Intel RealSense T265 トラッキングカメラパーツクラス。
Donkeycar v3.1.1 realsense2.py を書き換えたもの。
本コードはMITライセンス準拠とする。

1. donkeycar v3.1.1 をインストール
   https://github.com/autorope/donkeycar
2. librealsense をpythonラッパオプション付きでインストール
   https://github.com/IntelRealSense/librealsense
3. シャットダウンしT265をUSB(3.0推奨)接続してから再起動
4. 本コードを配置
5. manage.pyを修正
"""
import time
import logging
import math as m
import numpy as np
try:
    import pyrealsense2 as rs
except:
    print('[RealSenseT265] This module requires pyrealsense2 package!')
    raise

class FullDataReader:
    '''
    T265から取得可能な全データを取得するDonkey Partクラス。
    Donkeycar v3.1.1 上のコードをベースに作成。
    なお、外部車輪オドメトリ補正対応は行っていない。
    '''

    def __init__(self, image_output=False, debug=False):
        """
        RealSense T265トラッキングカメラからデータを取得するパーツクラス。
        引数：
            image_output    T265に搭載された2つの魚眼カメラのうち片方から
                            画像ストリームを取得する(USB3.0推奨)。
                            デフォルトはFalse、runを実行すると常にNoneが返却される。
            debug           デバッグフラグ。真値にすると標準出力にログを出力する。
        戻り値：
            なし
        """
        self.debug = debug
        self.image_output = image_output

        # RealSenseパイプラインを宣言し、実際のデバイスとセンサをカプセル化
        self.pipe = rs.pipeline()
        cfg = rs.config()
        cfg.enable_stream(rs.stream.pose)

        if self.image_output:
            # 現時点で両カメラを有効にする必要あり
            cfg.enable_stream(rs.stream.fisheye, 1) # 左カメラ
            cfg.enable_stream(rs.stream.fisheye, 2) # 右カメラ

        # 要求された校正でストリーミング開始
        self.pipe.start(cfg)

        # スレッド開始
        self.running = True
        
        zero_vec = (0.0, 0.0, 0.0)
        self.pos = zero_vec
        self.vel = zero_vec
        self.acc = zero_vec
        self.e_vel = zero_vec
        self.e_acc = zero_vec
        self.rot = (0.0, 0.0, 0.0, 0.0)
        self.ang = zero_vec
        self.posemap_conf = 0x0 # 失敗
        self.pose_conf = 0x0 # 失敗
        self.left_img = None
        self.right_img = None

    def poll(self):
        try:
            frames = self.pipe.wait_for_frames()
        except Exception as e:
            if self.debug:
                print(e)
            logging.error(e)
            return

        if self.image_output:
            # 左魚眼ガメラからイメージを取得する
            left = frames.get_fisheye_frame(1)
            self.left_img = np.asanyarray(left.get_data())
            # 右魚眼ガメラからイメージを取得する
            right = frames.get_fisheye_frame(2)
            self.right_img = np.asanyarray(right.get_data())


        # 位置情報フレームをフェッチ
        pose = frames.get_pose_frame()

        if pose:
            data = pose.get_pose_data()
            # 位置座標
            self.pos = (data.translation.x, data.translation.y, data.translation.z)
            # 速度
            self.vel = (data.velocity.x, data.velocity.y, data.velocity.z)
            # 加速度
            self.acc = (data.acceleration.x, data.acceleration.y, data.acceleration.z)
            # 角速度
            self.e_vel = (data.angular_velocity.x, data.angular_velocity.y, data.angular_velocity.z)
            # 角加速度
            self.e_acc = (data.angular_acceleration.x, data.angular_acceleration.y, data.angular_acceleration.z)
            # 四元数
            self.rot = (data.rotation.w, -data.rotation.z, data.rotation.x, -data.rotation.y)
            # オイラー角
            self.ang = self.get_eular_angle()
            # マップ信頼度：0x0-失敗、0x1-低、0x2-中、0x3-高
            self.posemap_conf = data.mapper_confidence
            # 位置座標信頼度：0x0-失敗、0x1-低、0x2-中、0x3-高
            self.pose_conf = data.tracker_confidence
            logging.debug('[RealSenseT265] poll() pos(%f, %f, %f)' % (self.pos[0], self.pos[1], self.pos[2]))
            #logging.debug('[RealSenseT265] poll() ang(%f, %f, %f)' % (self.ang[0], self.ang[1], self.ang[2]))
            if self.debug:
                print('[RealSenseT265] poll() pos(%f, %f, %f)' % (self.pos[0], self.pos[1], self.pos[2]))
                print('[RealSenseT265] poll() vel(%f, %f, %f)' % (self.vel[0], self.vel[1], self.vel[2]))
                print('[RealSenseT265] poll() ang(%f, %f, %f)' % (self.ang[0], self.ang[1], self.ang[2]))
                print('[RealSenseT265] poll() rot(%f, %f, %f, %f)' % (self.rot[0], self.rot[1], self.rot[2], self.rot[3]))
                print('[RealSenseT265] poll() eular vel(%f, %f, %f)' % (self.e_vel[0], self.e_vel[1], self.e_vel[2]))
                print('[RealSenseT265] poll() eular acc(%f, %f, %f)' % (self.e_acc[0], self.e_acc[1], self.e_acc[2]))
                print('[RealSenseT265] poll() conf map:%d pose:%d' % (self.posemap_conf, self.pose_conf))
                print('[RealSenseT265] poll() left is None:{} right is None:{}'.format(str(self.left_img is None), str(self.right_img is None)))
    def get_eular_angle(self):
        """
        インスタンス変数 `self.rot` （四元数）から姿勢角速度を算出する。
        引数：
            なし
        戻り値：
            (roll, pitch, yaw)  初期位置を基準としたオイラー角（ラジアン）
        """
        w, x, y, z = self.rot[0], self.rot[1], self.rot[2], self.rot[3]
        roll  =  m.atan2(2.0 * (w*x + y*z), w*w - x*x - y*y + z*z) * 180.0 / m.pi
        pitch =  -m.asin(2.0 * (x*z - w*y)) * 180.0 / m.pi
        yaw   =  m.atan2(2.0 * (w*z + x*y), w*w + x*x - y*y - z*z) * 180.0 / m.pi
        return (roll, pitch, yaw)

    def update(self):
        """
        別スレッドが生成されたら、このメソッドが呼び出される。
        T265からセンサデータを取得する。
        インスタンス変数runningが真である間、poll()を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        while self.running:
            self.poll()

    def run_threaded(self):
        """
        パーツクラスTemplate Methodのひとつ。threadedが真である場合、
        run()のかわりに呼び出される。
        T265で取得可能なすべての最新センサデータを返却する。
        最新センサデータは本メソッド実行時に取得していない（別スレッド
        により更新）。
        引数：
            なし
        戻り値：
            pos_x               位置情報X軸（単位：メートル）
            pos_y               位置情報Y軸（単位：メートル）
            pos_z               位置情報Z軸（単位：メートル）
            vel_x               速度X軸（単位：メートル/秒）
            vel_y               速度Y軸（単位：メートル/秒）
            vel_z               速度Z軸（単位：メートル/秒）
            e_vel_x             角速度X軸、gyr_xに相当（単位：ラジアン/秒）
            e_vel_y             角速度Y軸、gyr_yに相当（単位：ラジアン/秒）
            e_vel_z             角速度Z軸、gyr_zに相当（単位：ラジアン/秒）
            acc_x               加速度X軸（単位：メートル/秒^2）
            acc_y               加速度Y軸（単位：メートル/秒^2）
            acc_z               加速度Z軸（単位：メートル/秒^2）
            e_acc_x             角加速度X軸（単位：ラジアン/秒^2）
            e_acc_y             角加速度Y軸（単位：ラジアン/秒^2）
            e_acc_z             角加速度Z軸（単位：ラジアン/秒^2）
            rot_i               四元数(Qi)
            rot_j               四元数(Qj)
            rot_k               四元数(Qk)
            rot_l               四元数(Ql)
            ang_x               オイラー角X軸(ロール)（単位：ラジアン）
            ang_y               オイラー角Y軸(ピッチ)（単位：ラジアン）
            ang_z               オイラー角Z軸(ヨー)（単位：ラジアン）
            posemap_conf        poseマップ信頼度：0x0-失敗、0x1-低、0x2-中、0x3-高
            pose_conf           pose信頼度：0x0-失敗、0x1-低、0x2-中、0x3-高
            left_image_array    左カメライメージ(nd.array型、(800,848)形式)
            right_image_array   右カメライメージ(nd.array型、(800,848)形式)
        """
        return self.pos[0], self.pos[1], self.pos[2], \
            self.vel[0], self.vel[1], self.vel[2], \
            self.e_vel[0], self.e_vel[1], self.e_vel[2], \
            self.acc[0], self.acc[1], self.acc[2], \
            self.e_acc[0], self.e_acc[1], self.e_acc[2], \
            self.rot[0], self.rot[1], self.rot[2], self.rot[3], \
            self.posemap_conf, self.pose_conf , \
            self.ang[0], self.ang[1], self.ang[2], \
            self.left_img, self.right_img

    def run(self):
        """
        パーツクラスTemplate Methodのひとつ。threadedが偽である場合、
        run_threaded()のかわりに呼び出される。
        T265で取得可能なすべての最新センサデータ（本メソッド呼び出し時
        に取得）を返却する。
        引数：
            なし
        戻り値：
            pos_x               位置情報X軸（単位：メートル）
            pos_y               位置情報Y軸（単位：メートル）
            pos_z               位置情報Z軸（単位：メートル）
            vel_x               速度X軸（単位：メートル/秒）
            vel_y               速度Y軸（単位：メートル/秒）
            vel_z               速度Z軸（単位：メートル/秒）
            e_vel_x             角速度X軸、gyr_xに相当（単位：ラジアン/秒）
            e_vel_y             角速度Y軸、gyr_yに相当（単位：ラジアン/秒）
            e_vel_z             角速度Z軸、gyr_zに相当（単位：ラジアン/秒）
            acc_x               加速度X軸（単位：メートル/秒^2）
            acc_y               加速度Y軸（単位：メートル/秒^2）
            acc_z               加速度Z軸（単位：メートル/秒^2）
            e_acc_x             角加速度X軸（単位：ラジアン/秒^2）
            e_acc_y             角加速度Y軸（単位：ラジアン/秒^2）
            e_acc_z             角加速度Z軸（単位：ラジアン/秒^2）
            rot_i               四元数(Qi)
            rot_j               四元数(Qj)
            rot_k               四元数(Qk)
            rot_l               四元数(Ql)
            ang_x               オイラー角X軸(ロール)（単位：ラジアン）
            ang_y               オイラー角Y軸(ピッチ)（単位：ラジアン）
            ang_z               オイラー角Z軸(ヨー)（単位：ラジアン）
            posemap_conf        poseマップ信頼度：0x0-失敗、0x1-低、0x2-中、0x3-高
            pose_conf           pose信頼度：0x0-失敗、0x1-低、0x2-中、0x3-高
            left_image_array    左カメライメージ(nd.array型、(800,848)形式)
            right_image_array   右カメライメージ(nd.array型、(800,848)形式)
        """
        self.poll()
        return self.run_threaded()

    def shutdown(self):
        """
        パーツクラスTemplate Methodのひとつ。終了時処理。
        マルチスレッドループを閉じ、T265パイプを停止する。
        引数：
            なし
        戻り値：
            なし
        """
        self.running = False
        time.sleep(0.1)
        self.pipe.stop()


if __name__ == "__main__":
    c = FullDataReader(image_output=True, debug=True)
    while True:
        c.run()
        #print(pos)
        time.sleep(0.1)
    c.shutdown()
