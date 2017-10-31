
import SimpleCV as scv

class AVTImageGrabber(object):

    def __init__(self, cam_id):
        self._cam = scv.AVTCamera(cam_id)

    def grab_image(self):
        try:
            scv_im = self._cam.getImage()
            return scv_im
            #return scv_im.getNumpyCv2()
        except:
            print 'Timeout!'
            return None

    def __del__(self):
        self._cam.setupSyncMode()

if __name__ == '__main__':

    from Queue import Queue
    from flexvi.core.images import save_image

    g = AVTImageGrabber(0)

    im = g1.grab_image()
