import logging as log

import PIL.Image
import pygame

class Image(object):

    def ToPyImage(self):
        pass

    def ToPilImage(self):
        pass

    def ResizeCrop(self, image, size):
        pass


class PyCamImage(Image):

    def __init__(self, image):
        self.image_surface = image.copy()
        self.pil_image = None

    def Copy(self):
        return PyCamImage(self.image_surface.copy())

    def ToPygameSurface(self):
        return self.image_surface

    def ToPilImage(self):
        if self.pil_image is None:
            size = self.image_surface.get_size()
            image_string = pygame.image.tostring(self.image_surface, "RGBA")
            self.pil_image = PIL.Image.frombytes("RGBA", size, image_string)

        return self.pil_image

    def ResizeProportional(self, size):
        result_ratio = size[0] / size[1]
        image = self.image_surface
        log.debug('Resizing from image {}'.format(image.get_size()))
        image_ratio = image.get_width() / image.get_height()

        if result_ratio > image_ratio:
            # going to a wider aspect ratio, so the image height will be cropped
            width_ratio = float(size[0]) / float(image.get_width())
            resized_image = pygame.transform.smoothscale(image, (size[0], int(image.get_height() * width_ratio)))

            log.debug('Resized image {}'.format(resized_image.get_size()))

            extra_height = resized_image.get_height() - size[1]
            extra_top = int(extra_height / 2)

            cropped_image = pygame.Surface(size)
            cropped_image.blit(resized_image, (0, 0), (0, extra_top, size[0], extra_top + size[1]))
            self.image_surface = cropped_image

        else:
            # going to a narrower aspect ratio, so the image width will be cropped
            height_ratio = float(size[1]) / float(image.get_height())
            
            new_size = (int(image.get_width() * height_ratio), size[1])
            resized_image = pygame.transform.smoothscale(image, new_size)

            log.debug('Resized image {}'.format(resized_image.get_size()))

            extra_width = resized_image.get_width() - size[0]
            extra_left = int(extra_width / 2)

            cropped_image = pygame.Surface(size)
            cropped_image.blit(resized_image, (0, 0), (extra_left, 0, extra_left + size[0], size[1]))

            log.debug('Cropped image {}'.format(cropped_image.get_size()))

            self.image_surface = cropped_image

        log.debug('New image {}'.format(self.image_surface.get_size()))

    def Save(self, path):
        pygame.image.save(self.image_surface, path)
        
