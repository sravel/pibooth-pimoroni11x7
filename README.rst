=====================
pibooth-pimoroni11x7
=====================

|PythonVersions| |PypiPackage| |Downloads|

``pibooth-pimoroni11x7`` is a plugin for the `pibooth <https://github.com/pibooth/pibooth>`_
application.

Pibooth plugin to use Pimoroni led 11x7 `Pimoroni led 11x7  <https://shop.pimoroni.com/products/11x7-led-matrix-breakout>`_


Install
-------

::

    $ pip3 install pibooth-pimoroni11x7


Configuration
-------------

This is the extra configuration options that can be added in the ``pibooth``
configuration):

.. code-block:: ini

    [PIMORONI11x7]
    # Enable plugin
    activate = True
    
    # Message to display on wait state
    wait_message = hello from pibooth

.. note:: Edit the configuration by running the command ``pibooth --config``.


.. |PythonVersions| image:: https://img.shields.io/badge/python-2.7+ / 3.6+-red.svg
   :target: https://www.python.org/downloads
   :alt: Python 2.7+/3.6+

.. |PypiPackage| image:: https://badge.fury.io/py/pibooth-pimoroni11x7.svg
   :target: https://pypi.org/project/pibooth-pimoroni11x7
   :alt: PyPi package

.. |Downloads| image:: https://img.shields.io/pypi/dm/pibooth-pimoroni11x7?color=purple
   :target: https://pypi.org/project/pibooth-pimoroni11x7
   :alt: PyPi downloads
