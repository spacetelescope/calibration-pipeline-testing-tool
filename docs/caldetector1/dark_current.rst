***************
Dark Correction
***************

This step removes dark current from the science exposure by subtracting a dark current reference file. For MIRI, the
correction is integration dependent.

The dark-subtraction step uses dark reference files with NFRAMES=1 and GROUPGAP=0 (i.e., no averaging of frames into
groups and no dropping of frames). It averages and skips dark frames to match the NFRAMES and GROUPGAP values of the
science data, then performs a group-by-group subtraction of the dark data from the science data; extra dark frames are
ignored. If the science exposure contains more frames than the dark reference file, the pipeline issues a warning and
the entire dark subtraction process is skipped.

Table 3‑4 provides with the DQ flags  used to flag warm and hot pixels, which may change on short timescales, as well as
pixels with unreliable dark corrections. These flags are propagated into the PIXELDQ array of the science data.

When the optional parameter dark output is set to a file name, the frame-averaged dark reference data will be written to
the specified FITS file. Subarrays are handled by having CRDS return the dark reference file appropriate for the subarray mode.

For more details on this step refer to the JWST Science Pipelines Documentation at http://ssb.stsci.edu/doc/jwst_git/docs/dark_current/html/

Test Requirements
=================
This step requires verification only. The outcome of this step depends almost exclusively on the reference file used.
Darks should have enough S/N for all possible ramps for full frame and subarrays. The Guiders should be excluded from
this test. Guiders don't have darks from CV3 because of a large chamber background (5 to 10 ADU/second vs. ~0.01
ADU/second dark current expected).

========================================================================================================================= ===========================================================================
Requirement                                                                                                               Fulfilled by
========================================================================================================================= ===========================================================================
When there are less frames in the reference file than in the data, check that there is a warning and the step is skipped   ``~caltest.test_caldetector1.test_dark_current.test_dark_subtraction``
Check that when there are more frames in the dark reference file the extra frames are ignored.                             ``~caltest.test_caldetector1.test_dark_current.test_dark_subtraction``
Verify that when a dark has NaN, these are correctly assumed as zero and the PIXELDQ is set properly                       ``~caltest.test_caldetector1.test_dark_current.test_dark_subtraction``
Verify that the DQ array of the dark is correctly combined with the PIXELDQ array of the science data.                     ``~caltest.test_caldetector1.test_dark_current.test_pixeldq_propagation``
Verify that when the dark is not applied, the data is correctly flagged as such.
Verify the Dark correction is done by integration for MIRI observations.
========================================================================================================================= ===========================================================================

Test Procedure
==============

.. code-block:: bash

    test_pipeline --dark-current <input_data>

Reference/API
=============

.. automodapi:: caltest.test_caldetector1.test_dark_current

