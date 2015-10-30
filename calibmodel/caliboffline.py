from flexvi.calibration.cameracalib import CameraCalibrator
from flexvi.confmanager.cmcalib import CalibrationConfigManager

cm = CalibrationConfigManager()

imset = cm.get_chessboard_imageset('sw-cb-1')

c = CameraCalibrator(imset)
c.calibrate()
