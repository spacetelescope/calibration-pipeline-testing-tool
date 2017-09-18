***************************
Data Quality Initialization
***************************

The Data Quality (DQ) flags track problems in the data. In the initialization step, the PIXELDQ and/or GROUPDQ extension
are created. The PIXELDQ extension is filled with information from the static Data Quality mask (Bad Pixel mask
reference file) for the input dataset using a bitwise_or function. The GROUPDQ array is initialized to zero. The PIXELDQ
extension is a 2-D array that contains the pixel dependent flags that are the same for all groups and integrations
within an exposure, while the GROUPDQ extension is a 4-D array that stores flags that can vary from one group or
integration to the next and that will be populated by subsequent steps. For more details refer to  JWST-STScI-004355 and
the calibration pipeline online software documentation in http://ssb.stsci.edu/doc/jwst_git/docs/dq_init/html/.

Test Requirements
=================

====================================================================================== =======================================================================
Requirement                                                                             Fulfilled by
====================================================================================== =======================================================================
The PIXELDQ is initialized with the information from the reference file.                `~caltest.test_caldetector1.test_dq_init.test_pixeldq_initialization`
The GROUPDQ extensions are added to the data and all values are initialized zero.       `~caltest.test_caldetector1.test_dq_init.test_groupdq_initialization`
A DQ_DEF extension with the definition of DQ flags should be present in all products.   `~caltest.test_caldetector1.test_dq_init.test_dq_def_initialization`
Error array is a 4-D array initialized to zero.                                         `~caltest.test_caldetector1.test_dq_init.test_err_initialization`
====================================================================================== =======================================================================

Test Data
=========

The ``dq_init`` step is applied the same to all instruments and exposure types except the NIRSpec IRS2 mode; therefore,
we choose to test one NIRCam FULL frame image and one SUB640 subarray image.

.. todo:: Need NIRSpec IRS2.

Test Procedure
==============

To run these tests the ``config.json`` should contain the ``"dq_init"`` section for example:

.. code-block:: json

    {
        "dq_init": [
            "dq_init/jw82600004001_02101_00001_nrcb1_uncal.fits",
            "dq_init/jw82600011001_02103_00001_nrcb1_uncal.fits"
        ]
    }

Using the above ``config.json`` simply run:

.. code-block:: bash

    test_pipeline --config config.json

Reference/API
=============

.. automodapi:: caltest.test_caldetector1.test_dq_init
