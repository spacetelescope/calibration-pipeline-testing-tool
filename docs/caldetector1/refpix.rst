**************************
Reference Pixel Correction
**************************

This step corrects for drifts in the counts due to the readout electronics using the reference pixels.
The correction is done for each pixel from amplifier-to-amplifier in a given group and from group-to-group.
The drift per row or column (depending on the instrument) seems to be the same for all amplifiers and it seems
to also depend on the row/column being odd or even. The algorithm is different for NIR and MIR detectors. 
For more details on this steps refer to the CalWG documentation and the JWST Science Pipelines Documentation
at http://jwst-pipeline.readthedocs.io/en/latest/jwst/refpix/

Test Requirements
=================
====================================================== ===================================================================
 Requirement                                            Fulfilled by
====================================================== ===================================================================
Check that the RefPixStep runs without error           `~caltest.test_caldetector1.test_refpix.test_refpix_step`
Determine if the correction has been correctly applied `~caltest.test_caldetector1.test_refpix.test_linearity_correction`
