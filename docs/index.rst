JWST Calibration Pipeline Testing
+++++++++++++++++++++++++++++++++

This is the documentation for calibration-pipeline-testing-tool.

Installation
============
Create a JWST pipeline environment to install into and install `pytest-html`

.. code::

  conda create -n test_jwst --file http://ssb.stsci.edu/releases/jwstdp/0.7.8/latest-osx
  source activate test_jwst
  pip install pytest-html

.. code:: bash

  git clone https://github.com/spacetelescope/calibration-pipeline-testing-tool.git
  cd calibration-pipeline-testing-tool
  python setup.py install

Basic Usage
===========

To setup tests, you specify test input files in a JSON file, with an entry for each step.
You do not need to provide input for every step.  The below example shows all currently available steps.
Any of the step names can be omitted and tests associated with that step will be skipped.
Multiple FITS files can be supplied for any given step and the tests will be repeated for each supplied file.

.. code:: json

  {
      "dq_init": [
          "dq_init_input.fits"
      ],

      "saturation": [
          "saturation_input.fits"
      ],

      "superbias": [
          "superbias_input.fits"
      ],

      "dark_current": [
          "dark_current_input.fits"
      ],

      "refpix": [
          "refpix_input.fits"
      ],

      "linearity": [
          "linearity_input.fits"
      ],

      "rscd": [
          "rscd_input.fits"
      ],

      "lastframe": [
          "lastframe_input.fits"
      ],

      "jump": [
          "jump_input.fits"
      ],

      "ramp_fit": [
          "ramp_fit_input.fits"
      ]
  }

Then from the command line simply run

.. code:: bash

  test_pipeline --config confg.json

This will produce a ``summary.html`` file with the test results as well as plots if any are produced.  These files are saved based on the input filename and will be overwritten on subsequent runs, so it is advisable run the test suite in it's own directory.  
Note that this file and the associated plots will be saved in the current directory so it may be useful to run ``test_pipeline`` in a new directory.

Contributing
============

If you would like to contribute tests to the package see the :ref:`developer`.

CALDETECTOR1
============

.. toctree::
  :maxdepth: 1

  caldetector1/dq_init.rst
  caldetector1/saturation.rst
  caldetector1/superbias.rst
  caldetector1/linearity.rst
  caldetector1/dark_current.rst
  caldetector1/refpix.rst
  caldetector1/rscd.rst
  caldetector1/lastframe.rst
  caldetector1/jump.rst
  caldetector1/ramp_fit.rst
