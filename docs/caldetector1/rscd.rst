*******************************************
Reset Switch Charge Decay (RSCD) Correction
*******************************************

This step corrects for the slow adjustment of the reset FET to the asymptotic level after reset.  
The effect appears as a hook over the first ~5 frames and employs a double exponential fit.
For more details on this step refer to the JWST Science Pipelines Documentation at
http://jwst-pipeline.readthedocs.io/en/latest/jwst/rscd

Test Requirements
=================
====================================================== ===============================================================
 Requirement                                            Fulfilled by
====================================================== ===============================================================
 Make sure the RSCD_Step runs without error.            `~caltest.test_caldetector1.test_rscd.test_rscd_step`
 Check that nothing changes in the first integration.   `~caltest.test_caldetector1.test_rscd.test_first_integration`

