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


###########################################################################
# HOOK pibooth
###########################################################################
@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('PIMORONI11x7', 'activate', False,
                   "Enable plugin",
                   "Enable pimoroni", ['True', 'False'])
    cfg.add_option('PIMORONI11x7', 'wait_message', "hello from Pibooth",
                   "Message to display on wait state",
                   "Wait message", "")


@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Create the PiboothPimoroni11x7 instance."""
    app.pimoroni_11x7 = PiboothPimoroni11x7(activate=cfg.getboolean('PIMORONI11x7', 'activate'))
    if app.pimoroni_11x7.get_disable():
        LOGGER.info("delette %s" % app.pimoroni_11x7.get_disable())
        del app.pimoroni_11x7


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
        app.pimoroni_11x7.clear_and_write(message=cfg.get('PIMORONI11x7', 'wait_message'))


@pibooth.hookimpl
def state_wait_do(app, cfg):
    """
    Display wait view message.
    """
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        # Auto scroll using a thread
        app.pimoroni_11x7.auto_scroll(interval=1)


@pibooth.hookimpl
def state_preview_do(self, cfg, app):
    pygame.event.pump()  # Before blocking actions
    app.pimoroni_11x7.preview_countdown(cfg.getint('WINDOW', 'preview_delay'))


@pibooth.hookimpl
def state_capture_enter(app, cfg):
    """Ready to take a capture."""
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.flash()


@pibooth.hookimpl
def state_capture_exit(app, cfg):
    """A capture has been taken."""
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.flash()
        app.pimoroni_11x7.clear_and_write(message=get_translated_text('smile'))


@pibooth.hookimpl
def pibooth_cleanup(app):
    if hasattr(app, 'pimoroni_11x7'):
        app.pimoroni_11x7.clear()
        app.pimoroni_11x7.threading.cancel()


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

    def __init__(self, activate=True):
        """Initialize GoogleUpload instance"""
        self.activate = activate
        self.__DISABLE = False
        self.display = None
        try:
            super().__init__()
        except ImportError as e:
            self.__DISABLE = True
            LOGGER.warning("System not support 'Pimoroni11x7' this plugins is disable")
        if self.activate and not self.__DISABLE:
            # Avoid retina-searage!
            self.set_brightness(0.5)
            # Set the font
            self.set_font(font3x5)
            LOGGER.info("Plugin 'Pimoroni11x7' is enable")
        elif not self.activate:
            LOGGER.info("Plugin 'Pimoroni11x7' is disable")

    def get_disable(self):
        """to remove plugin from pibooth if not able"""
        return self.__DISABLE

    def clear_and_write(self, message):
        """Clear buffer and add new message
        :param message: message to display on buffer"""
        if self.activate and not self.__DISABLE:
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            self.set_brightness(0.5)
            formatted_text = str(message).replace('"', '') + "   "
            self.write_string(formatted_text, font=font5x7)  # Write out your message

    def wait_scroll(self, timeout):
        # Show the buffer
        self.show()
        # Scroll the buffer content
        self.scroll()
        sleep(timeout)

    def auto_scroll(self, interval=1):
        """Autoscroll with a thread.
        Automatically show and scroll the buffer according to the interval value.
        :param interval: Amount of seconds (or fractions thereof), not zero
        """
        LOGGER.debug("interval is %s", interval)
        if not self.display:
            # Start a loop thread
            self.display = threading.Thread(group=None, target=self.wait_scroll, name="display", args=(interval),
                                            kwargs={})
            self.display.start()

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
        self.display.stop()
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")
        first_loop = True
        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            remaining = int(timer.remaining() + 1)
            if first_loop:
                timer.start()  # Because first preview capture is longer than others
                first_loop = False
                self.clear_and_write("%s".format(remaining))
                # Start a timer thread
                threading.Timer(remaining, self.preview_countdown).start()
                # Show the buffer
                self.show()
            pygame.event.pump()
