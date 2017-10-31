import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import time

class ROSImageSubscriber:

    def __init__(self, name, q, namespace=''):
        self.name = name
        #self.callback = callback_func  
        self.q = q
        
    def spin(self):
    
        self.image_sub = rospy.Subscriber("/cam1/camera/image_raw", Image, self.put_data)
        rospy.init_node(self.name, anonymous=True)

        try:
            rospy.spin()
        except KeyboardInterrupt:
            print "Shutting %s down" % self.name
            
    def put_data(self, data):
        self.q.put(data)
        print q.qsize()
        
    
if __name__ == '__main__':

    bridge = CvBridge()       

    def worker(q):
        data = q.get()
        print time.time(), "Message received!", type(data) 
        im = bridge.imgmsg_to_cv2(data, "mono8")
        print type(im)
        
    #s = ROSImageSubscriber('rosim', callback, '/cam1')
    
    from Queue import Queue
    q = Queue()
    s = ROSImageSubscriber('rosim', q, '/cam1')
    s.spin()
