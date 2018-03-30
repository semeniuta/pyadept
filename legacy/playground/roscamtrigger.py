import os, sys
import time

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

sys.path.append(r'/home/alex/Desktop/CODE/phd-flexvi-packages/ka_components/python/')
sys.path.append(r'/home/alex/Desktop/CODE/phd-flexvi-packages/adeptcell-calibmodel/python/')
import kavision
import feedercalib

bridge = CvBridge()

# Very bad anad temporary solution
def grab():

    im = None

    def callback(data):
        im = bridge.imgmsg_to_cv2(data, "mono8")
        
    image_sub = rospy.Subscriber("/cam1/camera/image_raw", Image, callback)
    rospy.init_node('grabber_temp', anonymous=True, disable_signals=True)
    rospy.spin()
    rospy.signal_shutdown("")
    
    return im


if __name__ == '__main__':

    pass
