import rospy

from polled_camera.srv import GetPolledImage, GetPolledImageRequest, GetPolledImageResponse

#rospy.wait_for_service('request_image')

try:
    get_img = rospy.ServiceProxy('/cam1/request_image', GetPolledImage)
    im = get_img()
except rospy.ServiceException, e:
    print "Service call failed: %s"%e
