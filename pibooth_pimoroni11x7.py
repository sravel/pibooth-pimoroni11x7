import threading
import pibooth
from pibooth.utils import LOGGER
from time import sleep
from matrix11x7 import Matrix11x7
from matrix11x7.fonts import font3x5


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
    if not app.pimoroni_11x7.get_disable():
        del(app.pimoroni_11x7)


@pibooth.hookimpl
def state_wait_enter(app, cfg):
    """
    Display wait view message.
    """
    if not hasattr(app, 'pimoroni_11x7'):
        app.pimoroni_11x7 = PiboothPimoroni11x7(activate=cfg.getboolean('PIMORONI11x7', 'activate'))
        if not app.pimoroni_11x7.get_disable():
            del(app.pimoroni_11x7)
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        # Auto scroll using a thread
        app.pimoroni_11x7.auto_scroll(cfg.get('PIMORONI11x7', 'wait_message'))
        # app.pimoroni_11x7.scroll_message(cfg.getboolean('PIMORONI11x7', 'wait_message'))


@pibooth.hookimpl
def state_capture_enter(app, cfg):
    """Ready to take a capture."""
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.flash()


@pibooth.hookimpl
def state_capture_exit(app, cfg):
    """A capture has been taken."""
    if hasattr(app, 'pimoroni_11x7') and cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pimoroni_11x7.clear()


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
        """to remove plugin from pibooth menu"""
        return self.__DISABLE

    def scroll_message(self, message):
        if self.activate and not self.__DISABLE:
            self.set_brightness(0.5)
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            length = len(self.write_string(message))  # Write out your message
            self.show()  # Show the result
            sleep(0.5)  # Initial delay before scrolling

            length -= self.width

            # Now for the scrolling loop...
            while length > 0:
                self.scroll(1)  # Scroll the buffer one place to the left
                self.show()  # Show the result
                length -= 1
                sleep(0.02)  # Delay for each scrolling step

            sleep(0.5)  # Delay at the end of scrolling

    def auto_scroll(self, message=None, interval=0.02):
        """Autoscroll with a thread (recursive function).
        Automatically show and scroll the buffer according to the interval value.
        :param message: message to display on buffer
        :param interval: Amount of seconds (or fractions thereof), not zero
        """
        if self.activate and not self.__DISABLE:
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            self.set_brightness(0.5)
            self.write_string(message)  # Write out your message
            # Start a timer
            threading.Timer(interval, self.auto_scroll, [interval]).start()
            # Show the buffer
            self.show()
            # Scroll the buffer content
            self.scroll()

    def flash(self):
        """Simulate flash with all light on"""

        if self.activate and not self.__DISABLE:
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            for x in range(0, 11):
                for y in range(0, 7):
                    self.pixel(x, y, 1)
            self.show()
            sleep(2)
