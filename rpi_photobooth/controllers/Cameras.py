import logging as log

import PIL.Image
import os
import datetime

import gphoto2 as gp

import cv2
import cv
import numpy

import pygame
import pygame.camera
import pygame.surfarray

import pkg_resources

from . import Images

#
# Base classes
#

class Camera(object):
    """
    This is a base class for all camera implementations. Includes the concept of storage to allow derived classes
    to use
    """
    
    def __init__(self, storage):
        self.storage = storage

    def SetStorage(self, storage):
        """Sets the camera to use given storage on next photo taken"""
        self.storage = storage

    def TakePhoto(self):
        """Capture image from the camera source"""
        pass

class CameraStorage(object):
    """
    This is a base class for camera storage implementations. All cameras should use these interfaces to interact with
    the provided storage.

    Implements the concept of using an array to store photos. Actual type is determined by child class.
    """

    def __init__(self):
        self.images = []

    def AddPhoto(self, image):
        """Adds a new photo to storage. To be implemented by child class."""
        pass

    def GetPhotos(self):
        """Gives an array of all the stored photos."""
        return self.images

    def GetLast(self):
        """Gives the last image added to storage."""
        return self.images[-1]

    def DeleteLast(self):
        """Deletes the last image added to storage."""
        self.images.pop() 

    def Clear(self):
        self.images = []

#
# Implementations
# 

class WebcamCamera(Camera):
    """Works with using the given webcam as camera."""

    # Assumes the webcam and storage are both already setup correctly.
    def __init__(self, webcam, storage):
        super(WebcamCamera, self).__init__(storage)
        self.webcam = webcam

    def TakePhoto(self):
        """
        Takes a photo with the webcam. Throws RuntimeError if it fails to get an image. This could happen when 
        the webcam is not connected.

        Assumes the webcam is operational when this class is created.
        """

        ret, image = self.webcam.Read()
        if not ret:
            raise RuntimeError('Could not take a photo. Webcam read failed.')
        
        self.storage.AddPhoto(image)

class GPhotoCamera(Camera):

    def __init__(self, storage, tmp_dir):
        super(GPhotoCamera, self).__init__(storage)
        self.context = gp.Context()
        self.camera = gp.Camera()

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        self.tmp_dir = tmp_dir

        # Try get into the camera to see if it's present
        self.camera.init(self.context)
        self.camera.exit(self.context)

    def TakePhoto(self):
        log.info('Taking photo.')

        self.camera.init(self.context)
        path = self.camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
        log.debug('Captured image.')

        camera_file = self.camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL, self.context)
        save_path = os.path.join(self.tmp_dir, path.name)
        camera_file.save(save_path)
        self.camera.exit(self.context)

        self.storage.AddPhoto(Images.FileImage(save_path))
        log.debug('Finished taking photo.')


class FileSystemCameraStorage(CameraStorage):

    def __init__(self, directory):
        """
        Create an instance of FileSystemCameraStorage. Given directory will be created for storing images.
        The directory is only used as secondary storage. The actual references to images are kept in memory.

        Args:
            directory: (string) - Path to directory for storage.
        """

        super(FileSystemCameraStorage, self).__init__()

        self.directory = directory

        if not os.path.exists(directory):
            os.makedirs(directory)

    def AddPhoto(self, image):
        """
        Args:
            image: (PIL.Image) - Image to add to storage.
        """

        self.images.append(image) 
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")
        save_path = os.path.join(self.directory, '{}.jpg'.format(timestamp)) 

        log.debug('Saving image to {}'.format(save_path))

        image.Save(save_path)


class OpencvWebcam(object):
    """
    Driver for reading from webcam using OpenCV library
    """

    def __init__(self, camera_index, frame_size):
        """
        Args:
            camera_index: (int) - Index of the camera. Use 0 for default camera.
            frame_size: (tuple) - A tuple with (width, height) of the desired frame. Not all sizes are supported by 
                                  all cameras so be careful what you set this to.
        """

        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, frame_size[0])
        self.capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, frame_size[1])
        # Internet says this should be present but we get error when trying to execute.
        #self.capture.set(cv.CV_CAP_PROP_BUFFERSIZE, 3)
        self.camera_index = camera_index

    def Start(self):
        # Do a read to initialise the webcam
        ret, frame = self.capture.read()
        if not ret:
            raise WebcamException('Error occurred while reading from webcam')


    def Read(self):
        ret, frame = self.capture.read()
        if not ret:
            raise WebcamException('Error occurred while reading from webcam')
        
        # Do colour coversion, otherwise image will appear with funny colours.
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return ret, frame

class PygameWebcam(object):

    def __init__(self, camera_index, frame_size):
       pygame.camera.init()
       self.camera_index = camera_index
       self.frame_size = frame_size
       self.camera_surface = pygame.surface.Surface(frame_size)
       
    def Start(self):
        self.camera = pygame.camera.Camera('/dev/video{}'.format(self.camera_index), self.frame_size)
        self.camera.start()

    def Read(self):
        self.camera.get_image(self.camera_surface)
        return True, Images.PyCamImage(self.camera_surface) 

class DummyPygameWebcam(object):

    def __init__(self):
        self.image_index = 0
        self.images = []

        path = pkg_resources.resource_filename('rpi_photobooth.resources.images.webcam', 'frame1.jpg')
        image_surface = pygame.image.load(path)
        self.images.append(image_surface)

        path = pkg_resources.resource_filename('rpi_photobooth.resources.images.webcam', 'frame2.jpg')
        image_surface = pygame.image.load(path)
        self.images.append(image_surface)

    def Start(self):
        pass

    def Read(self):
        self.image_index = (self.image_index + 1) % len(self.images)
        return True, Images.PyCamImage(self.images[self.image_index])


class WebcamException(Exception):
    """
    Raise when some error has occurred with webcam operation
    """
    pass
