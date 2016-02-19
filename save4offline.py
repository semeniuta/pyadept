from avtgrab import AVTImageGrabber
from flexvi.core.images import save_image
import sys
from Queue import Queue

_, cam_conf, name = sys.argv

if cam_conf == 'stereo':
    cameras = [0, 1]
elif cam_conf == 'cam1':
    cameras = [0]
elif cam_conf == 'cam2':
    cameras = [1]
else:
    raise Exception('Invalid cameras configuration %s. Allowed: stereo, cam1, cam2' % cam_conf)       

grabbers = {i: AVTImageGrabber(i, Queue()) for i in cameras}

for i, g in grabbers.iteritems():
    g.grab_image()
    lr = 'left' if i == 0 else 'right'
    fname = '../DATA/IMG/SWInspect/%s_%s.png' % (name, lr)
    save_image(g.q.get(), fname)


