import numpy as np
import datetime
import os

from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image


default_settings = {
    'NIGHT_TWILIGHT_THRESHOLD': 90,
    'NIGHT_DARK_THRESHOLD': 50,
    'NIGHT_BLACK_THRESHOLD': 4,
    'SPACE_TARGET_MB': 100,
    'SPACE_TIMER_HOURS': 1,
    'SPACE_MEDIA_DIR': 'os.',
    'SPACE_TARGET_EXT': '.jpg',  # Make sure image format extention starts with a dot
    'IMAGE_FORMAT': '.jpg',  # Make sure image format extention starts with a dot

}

folder = os.path.join(os.getcwd(), 'images')
stream = BytesIO()
camera = PiCamera(resolution=(1920, 1440))
camera.start_preview()
sleep(2)

for _ in camera.capture_continuous(stream, format='jpeg'):
    # "Rewind" stream to the beginning so we can read its content
    stream.seek(0)
    image = Image.open(stream)
    # Calculate average pixel value for detemining day-twilight-night conditions
    pix_ave = int(np.average(image))
    filename = datetime.datetime.now().strftime('%a - %H-%M') + f' ({pix_ave})img.jpg'
    save_path = os.path.join(folder, filename)
    image.save(save_path)
    image.truncate()
    print('>>>>>', datetime.datetime.now(), f'{filename} captured', sep='     ')
    sleep(20) # wait 5 minutes

