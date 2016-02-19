import SimpleCV as scv

class AVTImageGrabber:

    def __init__(self, cam_id, q):
        self.cam = scv.AVTCamera(cam_id)
        self.q = q
        self.last_scv_im = None

    def grab_image(self):
        self.last_scv_im = self.cam.getImage()  
        self.q.put(self.last_scv_im.getNumpyCv2())
        
    def __del__(self):
        self.cam.setupSyncMode()

        
if __name__ == '__main__':

    from Queue import Queue
    from flexvi.core.images import save_image
    
    g1 = AVTImageGrabber(0, Queue())
    g2 = AVTImageGrabber(1, Queue())
    
    #p1_start = g1.cam.getAllProperties()
    
    g1.grab_image()
    g2.grab_image()
    
    save_image(g1.q.get(), 'im1.png')
    save_image(g2.q.get(), 'im2.png')
    
    #p1_end = g1.cam.getAllProperties()
    
    #for k, v0 in p1_start.iteritems():
    #    v1 = p1_end[k]
    #    if v0 != v1:
    #        print k, v0, v1  
    
    
