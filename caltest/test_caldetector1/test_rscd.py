import numpy as np
from jwst.rscd import RSCD_Step
from jwst import datamodels
import pytest
from astropy.io import fits
import os

@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_rscdstep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    # delete the output FITS file after this module is finished
    os.remove(fname)

def test_rscd_step(fits_input):
    """Make sure the RSCD_Step runs without error."""

    RSCD_Step.call(datamodels.open(fits_input), save_results=True)

def test_first_integration(fits_input, fits_output):
    """check that nothing changes in the first integration"""

    assert np.all(fits_input['SCI'].data[0] == fits_output['SCI'].data[0])