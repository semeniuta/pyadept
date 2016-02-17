import SimpleCV as scv

class AVTImageGrabber:

    def __init__(self, cam_id, q):
        self.cam = scv.AVTCamera(cam_id)
        self.q = q
        self.last_scv_im = None

    def grab_image(self):
        self.last_scv_im = self.cam.getImage()  
        q.put(self.last_scv_im.getNumpy())
        
        
if __name__ == '__main__':

    from Queue import Queue
    from flexvi.core.images import save_image
    
    q = Queue()
    g = AVTImageGrabber(3, q)
    
    
