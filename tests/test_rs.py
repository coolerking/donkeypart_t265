# -*- coding: utf-8 -*-
from time import sleep
import math
import numpy as np
import donkeycar as dk


def test_rs(cfg):
    """
    Donekycar v3.1.1 上のパーツクラスを使用。
    """
    V = dk.vehicle.Vehicle()

    from donkeycar.parts.realsense2 import RS_T265
    rs = RS_T265(image_output=True)
    V.add(rs, outputs=['pos', 'vel', 'acc', 'image_array'], threaded=False)

    class Split(object):
        def run(self, pos, vel, acc):
            return pos.x, pos.y, pos.z, vel.x, vel.y, vel.z, acc.x, acc.y, acc.z
        def shutdown(self):
            pass
    V.add(Split(), inputs=['pos', 'vel', 'acc'],
        outputs=['pos_x', 'pos_y', 'pos_z', 'vel_x', 'vel_y', 'vel_z', 'acc_x', 'acc_y', 'acc_z'])

    # image shape (800, 848)
    class ImageNoneCheck(object):
        def __init__(self, cfg):
            self.cfg = cfg
        def run(self, image_array):
            if image_array is None:
                #print('[RS] image_array is None')
                return np.zeros((self.cfg.IMAGE_H, self.cfg.IMAGE_W, self.cfg.IMAGE_DEPTH), dtype=np.uint8)
            else:
                #print('[RS] image.shape:{}'.format(str(image_array.shape)))
                return image_array
        def shutdown(self):
            pass
    V.add(ImageNoneCheck(cfg), inputs=['image_array'], outputs=['image_array'])

    class PrintRS(object):
        def run(self, image_array, pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, acc_x, acc_y, acc_z):
            #print((image_array is None))
            #print(type(image_array))
            #print(image_array.shape)
            #print('[RS] pos:({:.5g}, {:.5g}, {:.5g}) vel:({:.5g}, {:.5g}, {:.5g}) acc:({:.5g}, {:.5g}, {:.5g})'.format(
            print('{:.5g},{:.5g},{:.5g},{:.5g},{:.5g},{:.5g},{:.5g},{:.5g}, {:.5g}'.format(
                pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, acc_x, acc_y, acc_z))
        def shutdown(self):
            pass
    V.add(PrintRS(), inputs=['image_array', 'pos_x', 'pos_y', 'pos_z', 'vel_x', 'vel_y', 'vel_z', 'acc_x', 'acc_y', 'acc_z'])





    inputs=['image_array',
            'pos_x', 'pos_y', 'pos_z',
            'vel_x', 'vel_y', 'vel_z',
            'acc_x', 'acc_y', 'acc_z', 
        ]

    types=['image_array',
           'float', 'float', 'float',
           'float', 'float', 'float',
           'float', 'float', 'float',
        ]

    from donkeycar.parts.datastore import TubHandler
    th = TubHandler(path=cfg.DATA_PATH)
    tub = th.new_tub_writer(inputs=inputs, types=types, user_meta=[])
    V.add(tub, inputs=inputs, outputs=["tub/num_records"])

    try:
        V.start(rate_hz=cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.DRIVE_LOOP_HZ * 60) # 1min
            ## max_loop_count=cfg.MAX_LOOPS) # infinity
    except KeyboardInterrupt:
        print('exit')
    finally:
        print('done')

def test_rs2(cfg):
    """
    独自パーツを使用。
    """
    print('Use original T265 part class')
    V = dk.vehicle.Vehicle()
    V.mem['enc_vel_ms'] = 0.0
    from realsense2 import T265
    V.add(T265(image_output=True, debug=False),
        outputs=['pos_x', 'pos_y', 'pos_z',
            'vel_x', 'vel_y', 'vel_z',
            'gyr_x', 'gyr_y', 'gyr_z',
            'acc_x', 'acc_y', 'acc_z',
            'gyr_ax', 'gyr_ay', 'gyr_az',
            'rot_i', 'rot_j', 'rot_k', 'rot_l',
            'posemap_conf', 'pose_conf',
            'roll', 'pitch', 'yaw',
            'left_image_array', 'right_image_array'],
        threaded=True)

    # image shape (800, 848)
    class ImageNoneCheck(object):
        def __init__(self, cfg):
            self.cfg = cfg
        def run(self, image_array):
            if image_array is None:
                #print('[RS] image_array is None')
                return np.zeros((self.cfg.IMAGE_H, self.cfg.IMAGE_W, self.cfg.IMAGE_DEPTH), dtype=np.uint8)
            else:
                #print('[RS] image.shape:{}'.format(str(image_array.shape)))
                return image_array
        def shutdown(self):
            pass
    img_chk = ImageNoneCheck(cfg)
    V.add(img_chk, inputs=['left_image_array'], outputs=['left_image_array'])
    V.add(img_chk, inputs=['right_image_array'], outputs=['right_image_array'])

    class PrintT265:
        def __init__(self):
            print('pos_x,pos_y,pos_z,vel_x,vel_y,vel_z,gyr_x,gyr_y,gyr_z,acc_x,acc_y,acc_z,gyr_ax,gyr_ay,gyr_az,rot_i,rot_j,rot_k,rot_l,posemap_conf,pose_conf,roll,pitch,yaw')
        def run(self, pos_x, pos_y, pos_z,
        vel_x, vel_y, vel_z, 
        gyr_x, gyr_y, gyr_z, 
        acc_x, acc_y, acc_z, 
        gyr_ax, gyr_ay, gyr_az, 
        rot_i, rot_j, rot_k, rot_l, 
        posemap_conf, pose_conf, 
        roll, pitch, yaw):
            print('%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%f,%f,%f' % (pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, gyr_x, gyr_y, gyr_z, acc_x, acc_y, acc_z, gyr_ax, gyr_ay, gyr_az, rot_i, rot_j, rot_k, rot_l, posemap_conf, pose_conf, roll, pitch, yaw))
        def shutdown(self):
            pass
    V.add(PrintT265(),inputs=['pos_x', 'pos_y', 'pos_z',
            'vel_x', 'vel_y', 'vel_z',
            'gyr_x', 'gyr_y', 'gyr_z',
            'acc_x', 'acc_y', 'acc_z',
            'gyr_ax', 'gyr_ay', 'gyr_az',
            'rot_i', 'rot_j', 'rot_k', 'rot_l',
            'posemap_conf', 'pose_conf',
            'roll', 'pitch', 'yaw'])

    inputs=['left_image_array',
            'pos_x', 'pos_y', 'pos_z',
            'vel_x', 'vel_y', 'vel_z',
            'acc_x', 'acc_y', 'acc_z',
            'gyr_x', 'gyr_y', 'gyr_z',
            'roll', 'pitch', 'yaw',
        ]

    types=['image_array',
           'float', 'float', 'float',
           'float', 'float', 'float',
           'float', 'float', 'float',
           'float', 'float', 'float',
           'float', 'float', 'float',
        ]

    from donkeycar.parts.datastore import TubHandler
    th = TubHandler(path=cfg.DATA_PATH)
    tub = th.new_tub_writer(inputs=inputs, types=types, user_meta=[])
    V.add(tub, inputs=inputs, outputs=["tub/num_records"])

    try:
        V.start(rate_hz=cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.DRIVE_LOOP_HZ * 60) # 1min
            ## max_loop_count=cfg.MAX_LOOPS) # infinity
    except KeyboardInterrupt:
        print('exit')
    finally:
        print('done')

if __name__ == '__main__':
    cfg = dk.load_config()
    try:
        print('start')
        from realsense2 import T265
    except:
        print('Use donkeycar RS_265 class instead of original T265 class') 
        test_rs(cfg)
    else:
        test_rs2(cfg)
    finally:
        print('done')