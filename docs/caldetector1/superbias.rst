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

#. Check the bias is correctly subtracted for full frame and subarrays
#. Compare with or a standalone routine and check that is the same results.
#. Check that the PIXELDQ  array of the science exposure is correctly combined with the DQ array.

Test Data
=========

.. todo:: Determine test data including at least one subarray case.

Test Procedure
==============

.. code-block:: bash

    test_pipeline --dark-current <input_data>

Test Results
============

