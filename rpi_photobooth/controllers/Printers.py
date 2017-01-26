import logging as log

import cups
import os
import datetime
import time

import pygame

from . import Images

#
# Base classes
#

class PrintingService(object):

    def Start(self):
        pass

    def PrintImage(self, image):
        pass

#
# Printer implementations
# 

class CupsPrinter(PrintingService):
    """
    A printing service that uses the cups services in Linux for printing. 
    """

    def __init__(self, printer_name, working_dir, border_percentage=0):
        self.printer_name = printer_name
        self.border = border_percentage
        self.working_dir = working_dir
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)

        self.last_print_id = None

    def Start(self):
        self.conn = cups.Connection()

        printers = self.conn.getPrinters()
        if not self.printer_name in printers:
            raise PrintingException('Failed to find desired printer {}.'.format(self.printer_name))
            
        cups.setUser('pi')

    def PrintImage(self, image, copies=1):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")

        image_surface = image.ToPygameSurface()
        scale_factor = 1. + float(self.border) / 100.
        size = image_surface.get_size()
        size = tuple([int(scale_factor * x) for x in size])

        log.debug('Creating background surface {}'.format(size))

        background_surface = pygame.Surface(size)
        background_surface.fill((255, 255, 255))

        new_x = int(size[0] - image_surface.get_width()) / 2
        new_y = int(size[1] - image_surface.get_height()) / 2
        background_surface.blit(image_surface, (new_x, new_y))

        combined_image = Images.PyCamImage(background_surface)
        image_path = os.path.join(self.working_dir, 'ToPrint-{}.jpg'.format(timestamp))
        combined_image.Save(image_path)

        for i in range(0, copies):
            self.last_print_id = self.conn.printFile(self.printer_name, image_path, "Photobooth", {})
            log.info('Printed with job id {}'.format(self.last_print_id))

    def HasFinished(self):
        return (self.last_print_id and (self.conn.getJobs().get(self.last_print_id, None) is None))
            
class FilePrinter(PrintingService):
    """
    A printing service that saves the image to file instead.
    """

    def __init__(self, working_dir, delay_ms):
        self.working_dir = working_dir
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
        
        self.print_start = None
        self.delay = delay_ms

    def PrintImage(self, image):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")
        image_path = os.path.join(self.working_dir, 'ToPrint-{}.jpg'.format(timestamp))
        image.Save(image_path)

        self.print_start = time.time()

    def HasFinished(self):
        end = time.time()
        if self.print_start is not None and (end - self.print_start) * 1000 > self.delay:
            return True
        else:
            return False

#
# Other classes
# 

class PrintingException(Exception):
    pass
