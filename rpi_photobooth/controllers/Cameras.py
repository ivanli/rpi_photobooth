import logging as log

import PIL.Image
import os

# Base class for all camera implementations. Allows for basic storage and defines the interface.
class Camera(object):
    def __init__(self, storage):
        self.storage = storage

    def SetStorage(self, storage):
        self.storage = storage

    def TakePhoto(self):
        pass


# Works with using the given webcam as camera. 
class WebcamCamera(Camera):

    # Assumes the webcam and storage are both already setup correctly.
    def __init__(self, webcam, storage):
        super(WebcamCamera, self).__init__(storage)
        self.webcam = webcam

    def TakePhoto(self):
        ret, frame = self.webcam.Read()
        if not ret:
            raise RuntimeError('Could not take a photo. Webcam read failed.')
        
        img = PIL.Image.fromarray(frame)
        self.storage.AddPhoto(img)


# This class stores PIL images and allows clients to retrieve them.
class FileSystemCameraStorage:

    def __init__(self, directory):
        self.directory = directory
        self.images = []

        if not os.path.exists(directory):
            os.makedirs(directory)

    # CameraStorage interface
    def AddPhoto(self, image):
        self.images.append(image)

    # CameraStorage interface
    def GetPhotos(self):
        return self.images

    def GetLast(self):
        return self.images[-1]

    def DeleteLast(self):
        self.images.pop() 

    def Clear(self):
        """Clears the current images in work"""
        self.images = []
