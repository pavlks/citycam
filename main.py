import datetime
import logging
import os
import shutil
import time
import picamera
import numpy as np


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


camera = picamera.PiCamera()
camera.resolution = (4056, 3040)
camera.start_preview()
# Let camera warm-up
time.sleep(2)

folder = os.getcwd()
filename = datetime.datetime.now().strftime('%a - %H-%M') + '.jpg'  # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
print(folder, filename, sep='\n')

camera.capture(os.path.join(folder, filename))

total, used, free = shutil.disk_usage("/")

#------------------------------------------------------------------------------
def get_stream_pix_ave(streamData):
    '''
    Calculate the average pixel values for the specified stream
    used for determining day/night or twilight conditions
    '''
    pixAverage = int(np.average(streamData[..., 1]))
    return pixAverage

#------------------------------------------------------------------------------
def check_if_day_stream(currentDayMode, image):
    ''' Try to determine if it is day, night or twilight.'''
    dayPixAverage = 0
    currentDayMode = False
    dayPixAverage = get_stream_pix_ave(image)
    if dayPixAverage > NIGHT_TWILIGHT_THRESHOLD:
        currentDayMode = True
    return currentDayMode




#------------------------------------------------------------------------------
def filesToDelete(mediaDirPath, extension=IMAGE_FORMAT):
    '''
    Deletes files of specified format extension
    by walking folder structure from specified mediaDirPath
    '''
    return sorted(
        (os.path.join(dirname, filename)
         for dirname, dirnames, filenames in os.walk(mediaDirPath)
         for filename in filenames
         if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime, reverse=True)

#------------------------------------------------------------------------------
def freeSpaceUpTo(freeMB, mediaDir, extension=IMAGE_FORMAT):
    '''
    Walks mediaDir and deletes oldest files until SPACE_TARGET_MB is achieved.
    You should Use with Caution this feature.
    '''
    mediaDirPath = os.path.abspath(mediaDir)
    if os.path.isdir(mediaDirPath):
        MB2Bytes = 1048576  # Conversion from MB to Bytes
        targetFreeBytes = freeMB * MB2Bytes
        fileList = filesToDelete(mediaDir, extension)
        totFiles = len(fileList)
        delcnt = 0
        logging.info('Session Started')
        while fileList:
            statv = os.statvfs(mediaDirPath)
            availFreeBytes = statv.f_bfree*statv.f_bsize
            if availFreeBytes >= targetFreeBytes:
                break
            filePath = fileList.pop()
            try:
                os.remove(filePath)
            except OSError as err:
                logging.error('Del Failed %s', filePath)
                logging.error('Error is %s', err)
            else:
                delcnt += 1
                logging.info('Del %s', filePath)
                logging.info('Target=%i MB  Avail=%i MB  Deleted %i of %i Files ',
                             targetFreeBytes / MB2Bytes, availFreeBytes / MB2Bytes,
                             delcnt, totFiles)
                # Avoid deleting more than 1/4 of files at one time
                if delcnt > totFiles / 4:
                    logging.warning('Max Deletions Reached i of %i',
                                    delcnt, totFiles)
                    logging.warning('Deletions Restricted to 1/4 of '
                                    'total files per session.')
                    break
        logging.info('Session Ended')
    else:
        logging.error('Directory Not Found - %s', mediaDirPath)

#------------------------------------------------------------------------------
def freeDiskSpaceCheck(lastSpaceCheck):
    '''
    Perform Disk space checking and Clean up
    if enabled and return datetime done
    to reset ready for next sched date/time
    '''
    if SPACE_TIMER_HOURS > 0:   # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if (datetime.datetime.now() - lastSpaceCheck).total_seconds() > SPACE_TIMER_HOURS * 3600:
            lastSpaceCheck = datetime.datetime.now()
            if SPACE_TARGET_MB < 100:   # set freeSpaceMB to reasonable value if too low
                diskFreeMB = 100
            else:
                diskFreeMB = SPACE_TARGET_MB
            logging.info('SPACE_TIMER_HOURS=%i  diskFreeMB=%i  SPACE_MEDIA_DIR=%s SPACE_TARGET_EXT=%s',
                         SPACE_TIMER_HOURS, diskFreeMB, SPACE_MEDIA_DIR, SPACE_TARGET_EXT)
            freeSpaceUpTo(diskFreeMB, SPACE_MEDIA_DIR, SPACE_TARGET_EXT)
    return lastSpaceCheck%

