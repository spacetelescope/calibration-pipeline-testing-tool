************
Ramp Fitting
************

This step determines the mean count rate for each pixel by performing a linear fit to the jump-free ramp intervals for
each pixel. This is done via weighted ordinary least-squares method. For more information about this step refer the
JWST Science Calibration Pipeline documentation at http://jwst-pipeline.readthedocs.io/en/latest/jwst/ramp_fitting

Jump-free intervals are determined from the GROUPDQ array of the input data set, under the assumption that the jump step
has already flagged cosmic rays. Ramp intervals flagged as saturated are ignored.

Test Requirements
=================
=========================================================== =================================================================
 Requirement                                                 Fulfilled by
=========================================================== =================================================================
 Make sure the RampFitStep runs without error.               `~caltest.test_caldetector1.test_ramp_fit.test_ramp_fit_step`
 Check that output slope is close to the input slope.        `~caltest.test_caldetector1.test_ramp_fit.test_ramp_fit_slopes`
 Check that the ERR is the combined Poission and Readnoise.  `~caltest.test_caldetector1.test_ramp_fit.test_err_combination`
