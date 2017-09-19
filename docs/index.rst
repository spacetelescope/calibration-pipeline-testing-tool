JWST Calibration Pipeline Testing
+++++++++++++++++++++++++++++++++

This is the documentation for calibration-pipeline-testing-tool.

Installation
============
Create a JWST pipeline environment to install into

.. code::

  conda create -n test-0.7.8rc2 --file http://ssb.stsci.edu/releases/jwstdp/0.7.8/dev/jwstdp-0.7.8rc2-osx-py27.0.txt
  source activate test-0.7.8rc2

.. code:: bash

  git clone https://github.com/STScI-MESA/calibration-pipeline-testing-tool.git
  cd calibration-pipeline-testing-tool
  python setup.py install


CALDETECTOR1
============

.. toctree::
  :maxdepth: 1

  caldetector1/dq_init.rst
  caldetector1/saturation.rst
  caldetector1/superbias.rst
  caldetector1/linearity.rst
  caldetector1/dark_current.rst
