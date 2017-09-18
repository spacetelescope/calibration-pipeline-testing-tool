*********************
Superbias Subtraction
*********************

The superbias subtraction step removes the fixed detector bias from a science data set by subtracting a superbias
reference image.  This superbias is subtracted from every group in every integration of the science ramp data. Any NaN’s
present in the superbias image are set to zero before being subtracted from the science data. The superbias correction
should apply to subarray exposures. See Kevin Volk's presentation at the 5/31/2016 JWST Cal WG meeting.

For more details on this step refer to the JWST Science Pipelines Documentation at http://ssb.stsci.edu/doc/jwst_git/docs/superbias/html/

Test Requirements
=================
This step requires verification only. The outcome of this step depends almost exclusively on the reference file used.
Darks should have enough S/N for all possible ramps for full frame and subarrays. The Guiders should be excluded from
this test. Guiders don't have darks from CV3 because of a large chamber background (5 to 10 ADU/second vs. ~0.01
ADU/second dark current expected).

=============================================================================================== ========================================================================
 Requirement                                                                                     Fulfilled by
=============================================================================================== ========================================================================
 Check the bias is correctly subtracted.                                                         `~caltest.test_caldetector1.test_superbias.test_superbias_subtraction`
 Check that the PIXELDQ  array of the science exposure is correctly combined with the DQ array.  `~caltest.test_caldetector1.test_superbias.test_pixeldq_propagation`
=============================================================================================== ========================================================================

Test Data
=========

.. todo:: Determine test data including at least one subarray case.

Test Procedure
==============

To run these tests the ``config.json`` should contain the ``"superbias"`` section for example:

.. code-block:: json

    {
        "superbias": [
            "superbias/jw82600004001_02101_00001_nrcb1_dqinitstep_saturationstep.fits"
        ]
    }

Using the above ``config.json`` simply run:

.. code-block:: bash

    test_pipeline --config config.json

Reference/API
=============

.. automodapi:: caltest.test_caldetector1.test_superbias


