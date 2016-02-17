import sys, os
import cv2
import pandas as pd
import numpy as np
from skimage import measure, feature, util, draw, transform

from flexvi.core.images import open_image
from flexvi.core import ccomp
from flexvi.core.calibration import get_intrinsics_from_tuple
from flexvi.core.chessboard import find_chessboard_corners_on_image
from flexvi.core.homography import pt_homog_to_cart, pt_cart_to_homog

sys.path.append(r'/home/alex/CODE/phd-flexvi-packages/adeptcell-calibmodel/python/')
from feeder3pt import Feeder3PtCalibrator

sys.path.append(r'/home/alex/CODE/phd-flexvi-packages/ka_components/python/')
import kavision

im_cb = open_image('/home/alex/CODE/DATA/IMG/calib_3pt/cb3_bright.png')
im = open_image('/home/alex/Desktop/CODE/DATA/IMG/sw/test8.png')

psize = (19, 9)
sqsize = 10.0
frame = np.array([10.546, -695.157, 64.996, -73.294, 179.571, -73.027])

ti = pd.read_csv(os.path.join('/home/alex/CODE/phd-flexvi-packages/adeptcell-calibmodel/matlab/ti_2015-12-17', 'adept1_stereo1.csv'), index_col=0)
cm, dc = get_intrinsics_from_tuple(ti.ix[0])

c = Feeder3PtCalibrator(im_cb, psize, sqsize, cm, dc, frame)
c.calibrate()

labels, stats_df, imr = kavision.find_objects_on_feeder(im, 40)
df_good = kavision.get_objects_within_wh_range(stats_df, 40, 50, 40, 50)

res = []
for i in df_good.index:
    point = [df_good.ix[i].x, df_good.ix[i].y]
    wp = np.hstack((c.pixels_to_target(point), [0,1]))
    res.append(pt_homog_to_cart(wp))
    

''' MOVING THE ROBOT '''
    
from adeptagent import AdeptAgent
import config
import time

host = config.controller_ip
port = config.controller_port

agent = AdeptAgent(host, port)
agent.add_frame('feeder', frame)
agent.connect()

agent.move_dedicated("moveinterm")
agent.move_dedicated("closetofeeder")

for ind in [0]:
#for ind in range(len(res)):
    
    p = res[ind]
    
    agent.move_rel_frame('feeder', [p[0], p[1], 5, 0, 0, 0])
    agent.move_tool_z(3)
    agent.move_dedicated('gripper_open')
    agent.move_tool_z(-3)
      
agent.move_dedicated("closetofeeder")

