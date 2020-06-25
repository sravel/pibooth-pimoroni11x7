import threading
import pibooth
from pibooth.utils import LOGGER
from pibooth.language import get_translated_text
from matrix11x7 import Matrix11x7
from matrix11x7.fonts import font5x7
from time import sleep

__version__ = "1.0.0"

###########################################################################
# Grid buffer
###########################################################################
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

print_blink_grid = [
                [0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,1,1,1,1,0,0,0],
                [0,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0],
                [0,1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0],
                [0,1,0,1,1,1,1,1,0,1,0,0,1,0,1,1,1,1,1,0,1,0],
                [0,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0]]

###########################################################################
# HOOK pibooth
###########################################################################
@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options
    """
    cfg.add_option('PIMORONI11x7', 'enable', False,
                   "Enable plugin",
                   "Enable pimoroni", ['True', 'False'])
    cfg.add_option('PIMORONI11x7', 'brightness', 0.3,
                   "Message brightness",
                   "Message brightness", [str(x / 10.0 )for x in range(0, 11, 1)])
    cfg.add_option('PIMORONI11x7', 'wait_message', "hello from Pibooth",
                   "Message to display on wait state",
                   "Wait message", "")

#--- Startup  ---------------------------------------------------------------
@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Create the PiboothPimoroni11x7 instance.
    """
    app.pimoroni_11x7 = PiboothPimoroni11x7(config=cfg)
    
#--- Wait State ---------------------------------------------------------------
@pibooth.hookimpl
def state_wait_enter(app, cfg):
    """Write message to buffer.
    """
    app.pimoroni_11x7.clear_and_write(message=cfg.get('PIMORONI11x7', 'wait_message'))

@pibooth.hookimpl
def state_wait_do(app, cfg):
    """Display buffer message with scrolling.
    """
    app.pimoroni_11x7.scroll_display(interval=0.08)

#--- Choose State -------------------------------------------------------------
@pibooth.hookimpl
def state_choose_enter(app, cfg):
    """Write translated text of choose message to buffer.
    """
    app.pimoroni_11x7.clear_and_write(message=get_translated_text('choose'))

@pibooth.hookimpl
def state_choose_do(app, cfg):
    """Display buffer message with scrolling.
    """
    app.pimoroni_11x7.scroll_display(interval=0.05)

#--- Chosen State -------------------------------------------------------------
@pibooth.hookimpl
def state_chosen_enter(app, cfg):    
    """Write and display "GO" message.
    """
    app.pimoroni_11x7.clear_and_write(message="GO")
    app.pimoroni_11x7.scroll_display(interval=0)

#--- Preview State ------------------------------------------------------------
@pibooth.hookimpl
def state_preview_enter(app, cfg):
    """call threading to display countdown.
    """
    app.pimoroni_11x7.preview_countdown()

#--- Capture State ------------------------------------------------------------
@pibooth.hookimpl
def state_capture_enter(app, cfg):
    """If Flash is enable, use all led on, else write 0
    """
    if cfg.getboolean('WINDOW', 'flash'):
        app.pimoroni_11x7.flash()
    else:
        app.pimoroni_11x7.clear_and_write(message="0")
        app.pimoroni_11x7.scroll_display(interval=0)

@pibooth.hookimpl
def state_capture_exit(app, cfg):
    """remove display flash or 0
    """
    app.pimoroni_11x7.clear_and_write(message="")

#--- Processing State ---------------------------------------------------------
@pibooth.hookimpl
def state_processing_enter(app, cfg):
    """Write smile blink to buffer
    """
    app.pimoroni_11x7.draw_buffer(smile_blink_grid)
    
@pibooth.hookimpl
def state_processing_do(app, cfg):
    """Blink smile display
    """
    app.pimoroni_11x7.blink_scroll_display(interval=0.5)
    
@pibooth.hookimpl
def state_processing_exit(app, cfg):
    """Display heart
    """
    app.pimoroni_11x7.draw_buffer(heart_grid)

#--- PrintView State ----------------------------------------------------------
@pibooth.hookimpl
def state_print_enter(app, cfg):
    """Write print blink to buffer
    """
    app.pimoroni_11x7.draw_buffer(print_blink_grid)

@pibooth.hookimpl
def state_print_do(app, cfg):
    """Blink print display
    """
    app.pimoroni_11x7.blink_scroll_display(interval=0.5)

#--- Finish State -------------------------------------------------------------
@pibooth.hookimpl
def state_finish_enter(app, cfg):
    """Display heart
    """
    app.pimoroni_11x7.draw_buffer(heart_grid)


#--- Cleanup -------------------------------------------------------------
@pibooth.hookimpl
def pibooth_cleanup(app):
    """reset display
    """
    if not app.pimoroni_11x7._DISABLE:
        app.pimoroni_11x7.clear()
        app.pimoroni_11x7.show()


###########################################################################
# Class
###########################################################################
class PiboothPimoroni11x7(Matrix11x7):

    def __init__(self, config=None):
        """Initialize PiboothPimoroni11x7 instance
        :param config: pibooth config
        """
        self.config = config
        self._DISABLE = False
        self.check_ability_I2C()

        if self.check_enable():
            LOGGER.info("Plugin 'Pimoroni11x7' is enable")
        elif not self.check_enable():
            LOGGER.info("Plugin 'Pimoroni11x7' is disable")

    def check_ability_I2C(self):
        """use to disable the plugin if system not able to use I2C like raspberry pi
        """
        try:
            super().__init__()
        except ImportError as e:
            self._DISABLE = True
            LOGGER.warning("System not support I2C, 'Pimoroni11x7' plugins is disable")

    def check_enable(self):
        """test if plugin is active and I2C able
        """
        if self.config.getboolean('PIMORONI11x7', 'enable') and not self._DISABLE:      # enable and I2C able
            return True
        elif self._DISABLE:                                                             # I2C ERROR
            return False
        elif not self.config.getboolean('PIMORONI11x7', 'enable'):                      # disable plugin
            self.clear()
            self.show()
            return False

    def update_brightness(self):
        """update brightness if config change with menu
        """
        self.set_brightness(self.config.getfloat('PIMORONI11x7', 'brightness'))

    def clear_and_write(self, message):
        """Clear buffer and add new message
        :param message: message to display on buffer
        """
        if self.check_enable():
            self.clear() # Clear the display buffer and reset scrolling to (0, 0)
            self.show()  # apply to led
            self.update_brightness()
            formatted_text = str(message).replace('"', '') + "   "
            self.write_string(formatted_text, font=font5x7)

    def scroll_display(self, interval):
        """scroll buffer to 1 led with sleep time
        :param interval: time to sleep between scroll
        """
        if self.check_enable():
            self.show()
            self.scroll()
            sleep(interval)

    def blink_scroll_display(self, interval):
        """scroll buffer to 11 led with sleep time
           use by own own buffer build
        :param interval: time to sleep between scroll
        """
        if self.check_enable():
            self.show()
            self.scroll(11)
            sleep(interval)

    def draw_buffer(self, grid):
        """add own grid to buffer and see
        :param grid: tuple list to append to buffer with brightness value
        """
        if self.check_enable():
            self.update_brightness()
            self.clear()
            self.show()
            for x in range(0,len(grid[0])):
                for y in range(0,len(grid)):
                    self.set_pixel(x, y, grid[y][x])
            self.show(grid)

    def flash(self):
        """Simulate flash with all light on
        """
        if self.check_enable():
            self.clear()
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
         use threading.Time to synchronise with real capture time of camera
         """
        if self.check_enable():
            self.update_brightness()
            preview_delay = self.config.getint('WINDOW', 'preview_delay')
            countdown = preview_delay
            while countdown != 0:
                threading.Timer(0, self.run_threading_count, [countdown, preview_delay]).start()
                countdown -= 1


