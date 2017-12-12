**************
Jump Detection
**************

This step detects jumps (positive or negative, presumably due to cosmic rays) within an exposure by looking for outliers
in the up-the-ramp signal of all pixels in each integration within an exposure. When a jump is found, a cosmic-ray flag
is inserted into the 4-D GROUPDQ array at the location corresponding to the coordinates, group, and integration of the
affected pixel value. For more details refer to JWST-STScI-004355.

The baseline pipeline uses a  two-point difference method which is applied to all pixels in each integration.
The positions of the outliers or jumps are stored in the GROUPDQ array of the data. Subarray data uses the same
reference files as full frame. For more information about these Calibration Pipeline code refer to the JWST Science
Calibration Pipeline documentation at http://jwst-pipeline.readthedocs.io/en/latest/jwst/jump

Test Requirements
=================
=========================================================== ===============================================================
 Requirement                                                 Fulfilled by
=========================================================== ===============================================================
 Make sure the JumpStep runs without error.                  `~caltest.test_caldetector1.test_jump.test_jump_step`
 Check how well the Jump step detects injected cosmic rays.  `~caltest.test_caldetector1.test_jump.test_jump_performance`
