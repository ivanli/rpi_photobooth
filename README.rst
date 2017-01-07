===============================
Raspberry Pi Photobooth
===============================


.. image:: https://img.shields.io/pypi/v/rpi_photobooth.svg
        :target: https://pypi.python.org/pypi/rpi_photobooth

.. image:: https://img.shields.io/travis/ivanli/rpi_photobooth.svg
        :target: https://travis-ci.org/ivanli/rpi_photobooth

.. image:: https://readthedocs.org/projects/rpi-photobooth/badge/?version=latest
        :target: https://rpi-photobooth.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/ivanli/rpi_photobooth/shield.svg
     :target: https://pyup.io/repos/github/ivanli/rpi_photobooth/
     :alt: Updates


Photobooth application designed to execute on a Raspberry Pi with custom hardware


* Free software: MIT license
* Documentation: https://rpi-photobooth.readthedocs.io.


Features
--------

* TODO

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

## Project Structure (for the non-Python people)

Command line scripts exists in the `scripts` folder. The files are available through the command line when the package is
installed. An example might look like this:

```
#!/usr/bin/env python

import funniest
print funniest.joke()
```

They'll also need to be declared in the `setup.py` file like so:

```
setup(
    ...
    scripts=['bin/funniest-joke'],
    ...
)
```

# Setting Up Raspberry Pi

## XFCE

A better interface to use is XFCE. These are some issues that were resolved
during setup:

+ Wifi / Network indicator - Install `xfce4-indicator-plugin` to get the usual 
  indicators you'd expect.

## CUPS

This photobooth uses CUPS to connect to a printer and print. By default,
Pi only comes with gutenprint drivers 5.2.10, which was last updated in 2014. The
newer version (5.2.11) was updated in 2016 with lots of newer printers. 

The Canon SELPHY CP910 used here is supported in the latter version. To upgrade,
you'll need to build gutenprint from source.

Look at https://sourceforge.net/projects/gimp-print/files/gutenprint-5.2/5.2.11/ 
and download the .tar.bz2 source. Then run:

```
./configure
make
sudo make install
```

## Python Packages

Use `virtualenv` to manage your environment. The `virtualenvwrapper` package
contains useful shortcuts for creating and removing virtual environments.

The only way I could get the opencv package to read from a webcam is to install 
it via the system package. Usually the command is `apt-get install python-opencv`.

With the virtual environment, set it up with `mkvirtualenv --system-site-packages 
photobooth` to include installed system packages in the virtual environment.

Next, run `python setup.py develop` to install dependencies. Note that the `wx` 
dependency does not install via specifying it in setup.py, so it needs to be 
installed manually with `pip install wx`. This may take a while and you may need
to increase the swap memory of the Pi to allow successful building. Google
how to do this.


