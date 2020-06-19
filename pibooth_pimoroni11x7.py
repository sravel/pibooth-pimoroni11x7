import threading
import pibooth
from pibooth.utils import LOGGER
from pibooth.language import get_translated_text
from matrix11x7 import Matrix11x7
from matrix11x7.fonts import font5x7
from time import sleep

__version__ = "1.0.0"

smile_grid = [  [0,0,0,0,1,1,1,0,0,0,0],
                [0,0,0,1,0,0,0,1,0,0,0],
                [0,0,1,0,1,0,1,0,1,0,0],
                [0,0,1,0,0,0,0,0,1,0,0],
                [0,0,1,0,1,1,1,0,1,0,0],
                [0,0,0,1,0,0,0,1,0,0,0],
                [0,0,0,0,1,1,1,0,0,0,0]]

smile_blink_grid = [  [0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                      [0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0],
                      [0,0,1,0,1,0,1,0,1,0,0,0,0,1,0,1,0,0,0,1,0,0],
                      [0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0],
                      [0,0,1,0,1,1,1,0,1,0,0,0,0,1,0,1,1,1,0,1,0,0],
                      [0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0],
                      [0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0]]

heart_grid = [  [0,0,1,1,0,0,0,1,1,0,0],
                [0,1,1,1,1,0,1,1,1,1,0],
                [0,1,1,1,1,1,1,1,1,1,0],
                [0,0,1,1,1,1,1,1,1,0,0],
                [0,0,0,1,1,1,1,1,0,0,0],
                [0,0,0,0,1,1,1,0,0,0,0],
                [0,0,0,0,0,1,0,0,0,0,0]]

smile_heart_grid = [
                [0,0,0,0,1,1,1,0,0,0,0,0,0,1,1,0,0,0,1,1,0,0],
                [0,0,0,1,0,0,0,1,0,0,0,0,1,1,1,1,0,1,1,1,1,0],
                [0,0,1,0,1,0,1,0,1,0,0,0,1,1,1,1,1,1,1,1,1,0],
                [0,0,1,0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,1,1,0,0],
                [0,0,1,0,1,1,1,0,1,0,0,0,0,0,1,1,1,1,1,0,0,0],
                [0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                [0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0]]
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
    # app.pimoroni_11x7.clear_and_write(message=cfg.get('PIMORONI11x7', 'wait_message'))
    app.pimoroni_11x7.draw(smile_blink_grid)

@pibooth.hookimpl
def state_wait_do(app, cfg):
    """
    Display wait view message.
    """
    app.pimoroni_11x7.blink_scroll(interval=0.5)
    # app.pimoroni_11x7.wait_scroll(interval=0.08)

###########
# CHOOSE
##########
@pibooth.hookimpl
def state_choose_enter(app, cfg):
    app.pimoroni_11x7.clear_and_write(message=get_translated_text('choose'))

@pibooth.hookimpl
def state_choose_do(app, cfg):
    app.pimoroni_11x7.wait_scroll(interval=0.05)

###########
# CHOSEN
##########
@pibooth.hookimpl
def state_chosen_enter(app, cfg):
    app.pimoroni_11x7.clear_and_write(message="GO")
    app.pimoroni_11x7.wait_scroll(interval=0)

###########
# PREVIEW
##########
@pibooth.hookimpl
def state_preview_enter(app, cfg):
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
    app.pimoroni_11x7.draw(smile_grid)

@pibooth.hookimpl
def state_processing_exit(app, cfg):
    """
    """
    app.pimoroni_11x7.draw(heart_grid)


###########
# CLEANUP
##########
@pibooth.hookimpl
def pibooth_cleanup(app):
    if not app.pimoroni_11x7._DISABLE:
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
        """Initialize PiboothPimoroni11x7 instance
        :param config: pibooth config"""

        self.config = config
        
        self._DISABLE = False
        self.check_ability_I2C()

        if self.check_activate():
            LOGGER.info("Plugin 'Pimoroni11x7' is enable")
            self.set_font(font5x7)
            self.set_brightness(self.get_brightness())
        elif not self.check_activate():
            LOGGER.info("Plugin 'Pimoroni11x7' is disable")

    def check_ability_I2C(self):
        """use to disable the plugin if system not able to use I2C like raspberry pi"""
        try:
            super().__init__()
        except ImportError as e:
            self._DISABLE = True
            LOGGER.warning("System not support 'Pimoroni11x7' this plugins is disable")

    def check_activate(self):
        """test if plugin is active and able"""
        if self.config.getboolean('PIMORONI11x7', 'activate') and not self._DISABLE:
            return True
        elif self._DISABLE:
            return False
        else:
            self.clear()
            self.show()
            return False

    def get_brightness(self):
        """update brightness if config change with menu"""
        return self.config.getfloat('PIMORONI11x7', 'brightness')

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
        """scroll buffer to 1 led with sleep time
        :param interval: time to sleep between scroll"""
        if self.check_activate():
            self.show()          # Show the buffer
            self.scroll()        # Scroll the buffer content
            sleep(interval)

    def blink_scroll(self, interval):
        """scroll buffer to 11 led with sleep time
           use by own own buffer build
        :param interval: time to sleep between scroll"""
        if self.check_activate():
            self.show()          # Show the buffer
            self.scroll(11)        # Scroll the buffer content
            sleep(interval)

    def draw(self, grid):
        """add own grid to buffer and see
        :param grid: tuple list to append to buffer with brightness value"""
        if self.check_activate():
            self.set_brightness(self.get_brightness())
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            self.show()   # apply to led
            for x in range(0,len(grid[0])):
                for y in range(0,len(grid)):
                    self.set_pixel(x, y, grid[y][x])
            self.show(grid)

    def flash(self):
        """Simulate flash with all light on"""
        if self.check_activate():
            self.set_brightness(1)
            self.clear()  # Clear the display and reset scrolling to (0, 0)
            for x in range(0, 11):
                for y in range(0, 7):
                    self.pixel(x, y, 1)
            self.show()
 
    def run_threading_count(self, countdown, preview_delay):
        """function call by 'preview_countdown' thread to display countdown
           :param countdown: the countdown timer
           :param preview_delay: the start delay countdown
        """
        sleep(preview_delay-countdown)
        self.clear()
        pos_x = 3
        if countdown == 1:
            pos_x = 4
        self.write_string(str(countdown), x=pos_x, y=0, font=font5x7)  # Write out your message
        self.show()
        

    def preview_countdown(self):
        """Show a countdown of `timeout` seconds on the preview.
         use threading.Time to synchronise with real capture time of camera"""
        if self.check_activate():
            preview_delay = self.config.getint('WINDOW', 'preview_delay')
            countdown = preview_delay
            while countdown != 0:
                threading.Timer(0, self.run_threading_count, [countdown, preview_delay]).start()
                countdown -= 1


