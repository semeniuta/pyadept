import rospy
#from cv_bridge.CvBridge import imgmsg_to_cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import time

bridge = CvBridge()

def callback(data):
    print time.time(), "Message received!", type(data)
    
    im = bridge.imgmsg_to_cv2(data, "mono8")
    print type(im)

image_sub = rospy.Subscriber("/cam1/camera/image_raw", Image, callback)

rospy.init_node('rosim', anonymous=True)

try:
    rospy.spin()
except KeyboardInterrupt:
    print "Shutting down"
