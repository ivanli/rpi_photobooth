import logging as log

import PIL.Image
import os
import datetime

import gphoto2 as gp

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

        ret, frame = self.webcam.Read()
        if not ret:
            raise RuntimeError('Could not take a photo. Webcam read failed.')
        
        img = PIL.Image.fromarray(frame)
        self.storage.AddPhoto(img)

class GPhotoCamera(Camera):

    def __init__(self, storage, tmp_dir):
        super(GPhotoCamera, self).__init__(storage)
        self.context = gp.Context()
        self.camera = gp.Camera()
        self.camera.init(self.context)

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        self.tmp_dir = tmp_dir

    def __del__(self):
        self.camera.exit(self.context)

    def TakePhoto(self):
        path = self.camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
        camera_file = self.camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL, self.context)
        save_path = os.path.join(self.tmp_dir, path.name)
        camera_file.save(save_path)

        image = PIL.Image.open(save_path)
        self.storage.AddPhoto(image)


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
        save_path = os.path.join(self.directory, '{}.png'.format(timestamp)) 

        log.debug('Saving image to {}'.format(save_path))

        image.save(save_path)


