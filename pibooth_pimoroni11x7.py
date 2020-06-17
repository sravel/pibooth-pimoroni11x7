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
    app.pimoroni_11x7 = PiboothPimoroni11x7(activate=cfg.getboolean('PIMORONI11x7', 'activate'), brightness=cfg.getfloat('PIMORONI11x7', 'brightness'))
    if app.pimoroni_11x7.get_disable():
        LOGGER.info("delette %s" % app.pimoroni_11x7.get_disable())
        del app.pimoroni_11x7

###########
# WAIT
##########
@pibooth.hookimpl
def state_wait_enter(app, cfg):
    """
    Reset wait view message.
    """
    if not hasattr(app, 'pimoroni_11x7'):
        app.pimoroni_11x7 = PiboothPimoroni11x7(activate=cfg.getboolean('PIMORONI11x7', 'activate'))
        if app.pimoroni_11x7.get_disable():
            del (app.pimoroni_11x7)
    elif cfg.getboolean('PIMORONI11x7', 'activate'):
        # Auto scroll using a thread
        app.pimoroni_11x7.clear_and_write(message=cfg.get('PIMORONI11x7', 'wait_message'),brightness=cfg.getfloat('PIMORONI11x7', 'brightness'))

@pibooth.hookimpl
def state_wait_do(app, cfg):
    """
    Display wait view message.
    """
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        # Auto scroll using a thread
        # app.pimoroni_11x7.wait_scroll(interval=0.05)
        app.pimoroni_11x7.draw(smile_list)
    elif not cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.clear()

###########
# CHOOSE
##########
@pibooth.hookimpl
def state_choose_enter(app, cfg):
    if cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.clear_and_write(message=get_translated_text('choose'))

@pibooth.hookimpl
def state_choose_do(app, cfg):
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        # Auto scroll using a thread
        app.pimoroni_11x7.wait_scroll(interval=0.05)

###########
# CHOSEN
##########
@pibooth.hookimpl
def state_chosen_enter(app, cfg):
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.clear_and_write(message=get_translated_text('chosen'))
        # Auto scroll using a thread
        app.pimoroni_11x7.wait_scroll(interval=0.05)

###########
# PREVIEW
##########
@pibooth.hookimpl
def state_preview_do(app, cfg):
    pygame.event.pump()  # Before blocking actions
    app.pimoroni_11x7.preview_countdown(cfg.getint('WINDOW', 'preview_delay'))

###########
# CAPTURE
##########
@pibooth.hookimpl
def state_capture_enter(app, cfg):
    """Ready to take a capture."""
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.flash()


@pibooth.hookimpl
def state_capture_exit(app, cfg):
    """A capture has been taken."""
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.clear_and_write(message=get_translated_text('smile'))

###########
# CLEANUP
##########
@pibooth.hookimpl
def pibooth_cleanup(app):
    if hasattr(app, 'pimoroni_11x7'):
        app.pimoroni_11x7.clear()
        # app.pimoroni_11x7.display.cancel()


# @pibooth.hookimpl
# def state_processing_exit(app, cfg):
#     """
#     Generate the QR Code and store it in the application.
#     """
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

    def __init__(self, activate=True, brightness=0.3):
        """Initialize GoogleUpload instance"""
        self.activate = activate
        self.__DISABLE = False
        self.display = None
        self.brightness = brightness
        try:
            super().__init__()
        except ImportError as e:
            self.__DISABLE = True
            LOGGER.warning("System not support 'Pimoroni11x7' this plugins is disable")
        if self.activate and not self.__DISABLE:
            # Avoid retina-searage!
            self.set_brightness(self.brightness)
            # Set the font
            self.set_font(font3x5)
            LOGGER.info("Plugin 'Pimoroni11x7' is enable")
        elif not self.activate:
            LOGGER.info("Plugin 'Pimoroni11x7' is disable")

    def get_disable(self):
        """to remove plugin from pibooth if not able"""
        return self.__DISABLE

    def clear_and_write(self, message, brightness=0.3, activate=True):
        """Clear buffer and add new message
        :param message: message to display on buffer"""
        self.activate = activate
        self.brightness = brightness
        if self.activate and not self.__DISABLE:
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            self.set_brightness(self.brightness)
            formatted_text = str(message).replace('"', '') + "   "
            self.write_string(formatted_text, font=font5x7)  # Write out your message

    def wait_scroll(self, interval):
        # Show the buffer
        self.show()
        # Scroll the buffer content
        self.scroll()
        sleep(interval)

    def auto_scroll(self, interval=1):
        """Autoscroll with a thread.
        Automatically show and scroll the buffer according to the interval value.
        :param interval: Amount of seconds (or fractions thereof), not zero
        """
        LOGGER.debug("interval is %s", interval)
        # Start a loop thread
        # self.display = threading.Thread(group=None, target=self.wait_scroll, name="display", args=(interval),
        self.display = threading.Timer(interval, function=self.wait_scroll, args=[interval], kwargs=None)
        self.display.start()

    def draw(self, item):
        self.set_brightness(0.3)
        if self.activate and not self.__DISABLE:
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            for x, listy in enumerate(item):
                for y, state in enumerate(listy):
                    self.pixel(y, x, state)
            self.show()

    def flash(self):
        """Simulate flash with all light on"""
        self.set_brightness(1)
        if self.activate and not self.__DISABLE:
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            for x in range(0, 11):
                for y in range(0, 7):
                    self.pixel(x, y, 1)
            self.show()

    def preview_countdown(self, timeout):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished."""
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")
        first_loop = True
        timer = PoolingTimer(timeout)
        remaining = int(timer.remaining() + 1)
        if first_loop:
            timer.start()  # Because first preview capture is longer than others
            first_loop = False
        str_count = "%s".format(remaining)
        self.clear
        self.write_string(str_count, font=font5x7)  # Write out your message
        # Start a timer thread
        threading.Timer(1, self.preview_countdown, [remaining]).start()
        # Show the buffer
        self.show()
        pygame.event.pump()
