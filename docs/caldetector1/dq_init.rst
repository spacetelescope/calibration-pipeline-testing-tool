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
#.	The PIXELDQ is initialized with the information from the reference file.
#.	The GROUPDQ extensions are added to the data and all values are initialized zero.
#.	A DQ_DEF extension with the definition of DQ flags should be present in all products.
#.	Subarray exposures correctly extract the DQ values from the full frame reference file.
#.	Error array is a 4-D array initialized to zero.

Test Data
=========

.. todo:: Determine test data including at least one subarray case.

Test Procedure
==============

.. code-block:: bash

    test_pipeline --dq_init <input_data>

Test Results
============


