import os
import datetime
import time
import picamera

camera = picamera.PiCamera()
camera.resolution(1024, 768)
camera.start_preview()
# Let camera warm-up
time.sleep(2)

folder = os.path.abspath('/usr')
filename = datetime.datetime.now().strftime('%a - %H-%M') + '.jpg'  # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
camera.capture(os.path.join(folder, filename))
