****************
Saturation Check
****************

This step flags saturated pixels by going through all the groups and integrations within an exposure and comparing them
with the defined saturation threshold for each pixel, as given in the saturation reference file. The saturation limit
can refer to one of three thresholds:

* the threshold beyond which the linearity correction exceeds a particular accuracy requirement (e.g., 0.25% accuracy in the corrected value),

* the A/D saturation limit of 65535 ADU in the raw data, or

* the pixel full-well value.

At present, the pipeline does not distinguish among these thresholds. Header comments in the reference file should
indicate which threshold is employed. The saturation check is performed on data that have not been bias (first group)
subtracted, so saturation levels should be computed accordingly.



Test Requirements
=================
#. Check that the saturation flag is set when a pixel is above the threshold given by the reference file.
#. Once it is flagged as saturated in a group all subsequent groups should also be flagged as saturated.
#. Check that pixels in the reference files that have value NaN are not flagged as saturated in the data and that in the PIXELDQ array the pixel is set to NO_SAT_CHECK.
#. Check the step can handle full frame and subarrays

Test Data
=========

.. todo:: Determine test data including at least one subarray case.

Test Procedure
==============

.. code-block:: bash

    test_pipeline --saturation <input_data>

Test Results
============

