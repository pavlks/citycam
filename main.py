import os
import datetime
import time
import picamera

camera = picamera.PiCamera()
camera.resolution = (4056, 3040)
camera.start_preview()
# Let camera warm-up
time.sleep(2)

folder = os.getcwd()
filename = datetime.datetime.now().strftime('%a - %H-%M') + '.jpg'  # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
print(folder, filename, sep='\n')

camera.capture(os.path.join(folder, filename))
