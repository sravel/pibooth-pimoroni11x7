import os
from matrix11x7 import Matrix11x7
import pygame
import pibooth
from time import sleep

__version__ = "1.0.0"


###########################################################################
# HOOK pibooth
###########################################################################
@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('PIMORONI11x7', 'activate', True,
                   "Enable plugin",
                   "Enable pimoroni", ['True', 'False'])
    cfg.add_option('PIMORONI11x7', 'wait_message', "hello from Pibooth",
                   "Message to display on wait state",
                   "Wait message", "")

@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Create the PiboothPimoroni11x7 instance."""
    app.pibooth_pimoroni11x7 = PiboothPimoroni11x7(activate=cfg.getboolean('PIMORONI11x7', 'activate'))

@pibooth.hookimpl
def state_wait_enter(app, cfg):
    """
    Display wait view message.
    """
    if cfg.getboolean('PIMORONI11x7', 'activate'):
        app.pibooth_pimoroni11x7.scroll_message(cfg.getboolean('PIMORONI11x7', 'wait_message'))


# @pibooth.hookimpl
# def state_processing_exit(app, cfg):
#     """
#     Generate the QR Code and store it in the application.
#     """
#     qr = qrcode.QRCode(version=1,
#                        error_correction=qrcode.constants.ERROR_CORRECT_L,
#                        box_size=3,
#                        border=1)
#
#     name = os.path.basename(app.previous_picture_file)
#
#     if cfg.getboolean('QRCODE', 'by_photo'):
#         qr.add_data(os.path.join(cfg.get('QRCODE', 'url'), name))
#     else:
#         qr.add_data(cfg.get('QRCODE', 'url'))
#     qr.make(fit=True)
#
#     image = qr.make_image(fill_color=cfg.gettyped('QRCODE', 'color')[0],
#                           back_color=cfg.gettyped('QRCODE', 'color')[1]).convert('RGBA')
#     app.previous_qr = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
#
#
# @pibooth.hookimpl
# def state_print_enter(app, win, cfg):
#     """
#     Display the QR Code on the print view.
#     """
#     win_rect = win.get_rect()
#     qr_rect = app.previous_qr.get_rect()
#     if cfg.getboolean('QRCODE', 'activate'):
#         win.surface.blit(app.previous_qr, (win_rect.width - qr_rect.width - 10,
#                                            win_rect.height - qr_rect.height - 10))


###########################################################################
# Class
###########################################################################


class PiboothPimoroni11x7(Matrix11x7):

    def __init__(self, activate=True):
        """Initialize GoogleUpload instance"""
        self.activate = activate
        super(Matrix11x7, self).__init__()

    def scroll_message(self, message):
        self.clear()  # Clear the display and reset scrolling to (0, 0)
        length = self.write_string(message)  # Write out your message
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


