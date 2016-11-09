
import SimpleCV as scv

'''
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
'''

class AVTImageGrabber(object):

    def __init__(self, cam_id):
        self._cam = scv.AVTCamera(cam_id)

    def grab_image(self):
        scv_im = self._cam.getImage()
        return scv_im.getNumpyCv2()

    def __del__(self):
        self._cam.setupSyncMode()

if __name__ == '__main__':

    from Queue import Queue
    from flexvi.core.images import save_image

    g1 = AVTImageGrabber(0)
    g2 = AVTImageGrabber(1)

    #p1_start = g1.cam.getAllProperties()

    im1 = g1.grab_image()
    im2 = g2.grab_image()

    save_image(im1, 'im1.png')
    save_image(im2, 'im2.png')

    #p1_end = g1.cam.getAllProperties()

    #for k, v0 in p1_start.iteritems():
    #    v1 = p1_end[k]
    #    if v0 != v1:
    #        print k, v0, v1
