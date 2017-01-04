
import cups
import os
import datetime

class PrintingService(object):

    def Start(self):
        pass

    def PrintImage(self, image):
        pass

class CupsPrinter(PrintingService):
    """
    A printing service that uses the cups services in Linux for printing. 
    """

    def __init__(self, printer_name, working_dir):
        self.printer_name = printer_name
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

    def PrintImage(self, image):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")
        image_path = os.path.join(self.working_dir, 'ToPrint-{}.png'.format(timestamp))
        image.save(image_path)
        self.last_print_id = self.conn.printFile(self.printer_name, image_path, "Photobooth", {})

    def HasFinished(self):
        return (self.last_print_id and (self.conn.getJobs().get(self.last_print_id, None) is None))
            

class PrintingException(Exception):
    pass
