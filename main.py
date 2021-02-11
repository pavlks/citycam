import numpy as np
import datetime
import os
import cv2

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
    'MINIMUM_AREA': 100,  # Motion detection area. If smaller, will ignore

}

def process_frame(src_frame, prev_frame, minimum_area):
    height, width = src_frame.shape[:2]
    new_dim = (500, 500 * height / width)  # calculating new dimensions for resizing
    frame = cv2.resize(src_frame, new_dim, cv2.INTER_AREA)  # resizing the frame
    curr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # applying black and white filter
    curr_frame = cv2.GaussianBlur(gray, (21, 21), 0)  # applying blur

    # if the first frame is None, initialize it because there is no frame for comparing the current one with a previous one
    if prev_frame is None:
        prev_frame = curr_frame
        return prev_frame

    # check if past_frame and current have the same sizes. This shouldnt occur but this is error handling
    if prev_frame.shape[:2] != curr_frame.shape[:2]:
        print('Previous frame and current frame do not have the same sizes')
        print(f'{prev_frame.shape[:2]} != {curr_frame.shape[:2]}')
        return

    # computing the absolute difference between the current frame and previous frame
    frame_diff = cv2.absdiff(prev_frame, curr_frame)
    # applying a threshold to remove camera motion and other false positives
    thresh = cv2.threshold(frame_diff, 50, 255, cv2.THRESH_BINARY)
    # dilate the threshold image to fill in holes, then find contours on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = contours[0]

    for ct in cnts:
        if ct > default_settings['MINIMUM_AREA']:
            print('Motion detected')

if __name__ == '__main__':
    camera.resolution = (640, 480)
    prev_frame = None
    print('Starting motion detection')
    try:
        while True:
            stream = BytesIO()
            camera.capture(stream, format='jpeg', use_video_port=False)
            data = np.fromstring(stream.getvalue(), dtype=np.uint8)
            frame = cv2.imdecode(data, 1)
            if frame is not None:
                prev_frame = process_frame(frame, prev_frame, default_settings['MINIMUM_AREA'])
            else:
                print('No more frames')
    finally:
        print('Exiting...')

'''
folder = os.path.join(os.getcwd(), 'images')
stream = BytesIO()
camera = PiCamera(resolution=(1920, 1440))
camera.start_preview()
sleep(2)

for _ in camera.capture_continuous(stream, format='jpeg'):
    image = Image.open(stream)
    # Calculate average pixel value for detemining day-twilight-night conditions
    pix_ave = int(np.average(image))
    filename = datetime.datetime.now().strftime('%Y-%m-%d - %a - %H-%M-%S') + f' ({pix_ave})img.jpg'
    save_path = os.path.join(folder, filename)
    rotated = image.rotate(90)
    rotated.save(save_path)
    # image.save(save_path)
    print(':::::', datetime.datetime.now(), f'{filename} captured', sep='     ')
    # wait 5 minutes
    sleep(5*60)  
    # "Rewind" stream to the beginning so we can read its content
    stream.seek(0)
    stream.truncate()
'''
