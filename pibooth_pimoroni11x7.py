import threading
import pygame
import pibooth
from pibooth.utils import LOGGER
from pibooth.utils import PoolingTimer
from pibooth.language import get_translated_text
from matrix11x7 import Matrix11x7
from matrix11x7.fonts import font3x5, font5x7
from time import sleep

__version__ = "1.0.0"

smile_list = [  [0,0,0,0,1,1,1,0,0,0,0],
                [0,0,0,1,0,0,0,1,0,0,0],
                [0,0,1,0,1,0,1,0,1,0,0],
                [0,0,1,0,0,0,0,0,1,0,0],
                [0,0,1,0,1,1,1,0,1,0,0],
                [0,0,0,1,0,0,0,1,0,0,0],
                [0,0,0,0,1,1,1,0,0,0,0]]


###########################################################################
# HOOK pibooth
###########################################################################
@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('PIMORONI11x7', 'activate', False,
                   "Enable plugin",
                   "Enable pimoroni", ['True', 'False'])
    cfg.add_option('PIMORONI11x7', 'brightness', 0.3,
                   "Message brightness",
                   "Message brightness", [str(x / 10.0 )for x in range(0, 11, 1)])
    cfg.add_option('PIMORONI11x7', 'wait_message', "hello from Pibooth",
                   "Message to display on wait state",
                   "Wait message", "")

###########
# Startup
##########
@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Create the PiboothPimoroni11x7 instance."""
    app.pimoroni_11x7 = PiboothPimoroni11x7(config=cfg)
    
###########
# WAIT
##########

@pibooth.hookimpl
def state_wait_enter(app, cfg):
    if not hasattr(app, 'pimoroni_11x7'):
        app.pimoroni_11x7 = PiboothPimoroni11x7(config=cfg)
    else:
        app.pimoroni_11x7.config = cfg
        app.pimoroni_11x7.clear_and_write(message=cfg.get('PIMORONI11x7', 'wait_message'))

@pibooth.hookimpl
def state_wait_do(app, cfg):
    """
    Display wait view message.
    """
    if not hasattr(app, 'pimoroni_11x7'):
        app.pimoroni_11x7 = PiboothPimoroni11x7(config=cfg)
    else:
        app.pimoroni_11x7.config = cfg
        app.pimoroni_11x7.wait_scroll(interval=0.05)


###########
# CHOOSE
##########
@pibooth.hookimpl
def state_choose_enter(app, cfg):
    app.pimoroni_11x7.config = cfg
    app.pimoroni_11x7.clear_and_write(message=get_translated_text('choose'))

@pibooth.hookimpl
def state_choose_do(app, cfg):
    app.pimoroni_11x7.config = cfg
    app.pimoroni_11x7.wait_scroll(interval=0.05)

###########
# CHOSEN
##########
@pibooth.hookimpl
def state_chosen_enter(app, cfg):
    app.pimoroni_11x7.config = cfg
    app.pimoroni_11x7.clear_and_write(message="GO")
    app.pimoroni_11x7.wait_scroll(interval=0.05)

###########
# PREVIEW
##########
@pibooth.hookimpl
def state_preview_enter(app, cfg):
    app.pimoroni_11x7.config = cfg
    app.pimoroni_11x7.preview_countdown()

###########
# CAPTURE
##########
@pibooth.hookimpl
def state_capture_enter(app, cfg):
    """Ready to take a capture."""
    app.pimoroni_11x7.flash()


@pibooth.hookimpl
def state_capture_exit(app, cfg):
    """A capture has been taken."""
    app.pimoroni_11x7.clear_and_write(message=get_translated_text('smile'))

###########
# processing
##########
@pibooth.hookimpl
def state_processing_enter(app, cfg):
    """
    """
    app.pimoroni_11x7.draw(smile_list)

###########
# CLEANUP
##########
@pibooth.hookimpl
def pibooth_cleanup(app):
    if hasattr(app, 'pimoroni_11x7'):
        app.pimoroni_11x7.clear()
        app.pimoroni_11x7.show()



#
#
#
# @pibooth.hookimpl
# def state_print_enter(app, win, cfg):
#     """
#     Display the QR Code on the print view.
#     """


###########################################################################
# Class
###########################################################################

DISPLAY_WIDTH = width = 11
DISPLAY_HEIGHT = height = 7


class PiboothPimoroni11x7(Matrix11x7):

    def __init__(self, config=None):
        """Initialize PiboothPimoroni11x7 instance"""
        
        self.config = config
        self.activate = self.config.getboolean('PIMORONI11x7', 'activate')
        self._DISABLE = False
        self.count = None
        self.message = self.config.get('PIMORONI11x7', 'wait_message')

        try:
            super().__init__()
        except ImportError as e:
            self._DISABLE = True
            LOGGER.warning("System not support 'Pimoroni11x7' this plugins is disable")
        if self.activate and not self._DISABLE:
            LOGGER.info("Plugin 'Pimoroni11x7' is enable")
            self.set_font(font3x5)
            self.set_brightness(self.get_brightness())
        elif not self.activate:
            LOGGER.info("Plugin 'Pimoroni11x7' is disable")
    
    def check_activate(self):
        if self.config.getboolean('PIMORONI11x7', 'activate') and not self._DISABLE:
            return True
        else:
            self.clear()
            self.show()
            return False

    def get_brightness(self):
        return self.config.getfloat('PIMORONI11x7', 'brightness')
        

    def get_disable(self):
        """to remove plugin from pibooth if not able"""
        return self._DISABLE

    def clear_and_write(self, message):
        """Clear buffer and add new message
        :param message: message to display on buffer"""
        
        if self.check_activate():
            self.clear()  # Clear the display buffer and reset scrolling to (0, 0)
            self.show()   # apply to led
            self.set_brightness(self.get_brightness())
            formatted_text = str(message).replace('"', '') + "   "
            self.write_string(formatted_text, font=font5x7)  # Write out your message

    def wait_scroll(self, interval):
        self.show()          # Show the buffer
        self.scroll()        # Scroll the buffer content
        sleep(interval)

    def draw(self, item):
        self.set_brightness(self.get_brightness())
        if self.check_activate():
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            self.show()   # apply to led
            for x, listy in enumerate(item):
                for y, state in enumerate(listy):
                    self.pixel(y, x, state)
            self.show()

    def flash(self):
        """Simulate flash with all light on"""
        self.set_brightness(1)
        if self.count:
            self.count.cancel()
        if self.check_activate():
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            for x in range(0, 11):
                for y in range(0, 7):
                    self.pixel(x, y, 1)
            self.show()
 
    def run_count(self, preview_delay, countdown):
        sleep(countdown-preview_delay)
        str_count = str(preview_delay)
        self.clear()
        self.write_string(str_count, font=font5x7)  # Write out your message
        self.show()
        

    def preview_countdown(self):
        """Show a countdown of `timeout` seconds on the preview."""
        preview_delay = self.config.getint('WINDOW', 'preview_delay')
        countdown = preview_delay
        while preview_delay != 0:
            threading.Timer(0, self.run_count, [preview_delay, countdown]).start()
            preview_delay -= 1

