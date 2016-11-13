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

