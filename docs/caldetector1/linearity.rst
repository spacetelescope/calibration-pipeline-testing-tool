********************
Linearity Correction
********************

This step corrects for the detector non-linearity. The algorithm used to perform the linearity correction is described
in JWST-STScI-004355. CalWG states that the linearity correction should be dependent on wavelength with predictions that
at wavelengths greater than approximately 21 microns the non-linearity will be different than for shorter wavelengths.  
There is one reference file for all filters with wavelengths less than 21 microns and different files for each filter
about 21 microns (imager and coronagraphy).   For the LRS and MRS, there will be one file per grating setting.
 
For grouped data, the linearity correction derived from non-grouped data should be applied.  The algorithm used to
perform the linearity correction is described in JWST-STScI-004355. from SOCCER.

Pixels flagged as saturated are ignored. Data quality flags are also propagated from the DQ extension of the linearity
reference file (Table 3‑3) into the 2-D PIXELDQ array of the science data.

The correction is applied for each exposure pixel-by-pixel, group-by-group, and integration-by-integration. If a pixel
has at least one coefficient with NaN, it will not have the correction applied. Likewise, pixels that are marked as
saturated within a group or flagged with NO_LIN_CORR (linearity correction not determined for pixel) will not be
corrected.  In the case of subarrays and where there is not a specific reference file available, the pipeline will
extract a matching subarray from the full frame reference file data. For more details on this step refer to the JWST
Science Pipelines Documentation at http://ssb.stsci.edu/doc/jwst_git/docs/linearity/html/


Test Requirements
=================
#. Independently for MIR and NIR data:
    * Check that there are unique reference files for the different wavelength ranges and optical elements mentioned above (MIRI)
    * Use simulated data/real data and a standalone code or IDT’s code compare with what you get with the pipeline. Check that the multiplication is done correctly.
    * Repeat for observations at different wavelengths (MIRI).
#. Repeat this for subarray
#. Check it works for grouped and un-grouped data.
#. Check that the DQ flags are propagated correctly.
#. Validation Part 2: Use IDT pipeline and calculate the differences
#. Validation Part 2: Determine the Linearity Correction error
#. Validation Part 2: Check the accuracy near the saturation value. If it passes this test the saturation step is done correctly.

Test Data
=========

.. todo:: Determine test data including at least one subarray case.

Test Procedure
==============

.. code-block:: bash

    test_pipeline --linearity <input_data>

Test Results
============

