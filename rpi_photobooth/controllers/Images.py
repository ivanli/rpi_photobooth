
class Image(object):

    def ToPyImage(self):
        pass

    def ToPilImage(self):
        pass

class PyCamImage(Image):

    def __init__(self, image):
        self.image_surface = image.copy()

    def ToPygameSurface(self):
        return self.image_surface

    def ToPilImage(self):
        raise Exception('Not supported')

        
