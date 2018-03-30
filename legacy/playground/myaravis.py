'''

BAD IMPLEMENTATION!


(https://github.com/TheImagingSource/tiscamera/issues/18)
    Create a stream
    Register callback function
    Set acquisition mode to continuous
    Activate Trigger Mode
    Start acquisition
    Send Trigger Command to capture image

'''

from gi.repository import Aravis as ar
from gi.repository.GObject import Signal

def new_buffer_cb(stream, data):
    buffer = stream.try_pop_buffer()
    if buffer is not None:
        print buffer
        stream.push_buffer(buffer)
    
    
    
# Create a stream
cam = ar.Camera()
st = cam.create_stream()

# Register callback function
st.connect("new-buffer", new_buffer_cb, None)

# Set acquisition mode to continuous
cam.set_acquisition_mode(ar.AcquisitionMode.CONTINUOUS)

# Activate Trigger Mode
cam.set_trigger("Software")

# Start acquisition
cam.start_acquisition()

# Send Trigger Command to capture image
cam.software_trigger()

#st.push_buffer(ar.Buffer())
#cam.stop_acquisition()
