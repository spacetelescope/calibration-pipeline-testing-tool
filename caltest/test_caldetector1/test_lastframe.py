import numpy as np
from jwst.lastframe import LastFrameStep
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

def test_lastframe_step(fits_input):
    """Make sure the LastFrameStep runs without error."""

    LastFrameStep.call(datamodels.open(fits_input), save_results=True)

def test_lastframe_flagged(fits_input, fits_output):
    """
    check that GROUPDQ lastframe is flagged as DO_NOT_USE
    unless there is only 1 group
    """

    if fits_output['SCI'].data.shape[1] > 1:
        assert np.all(fits_output['GROUPDQ'].data[:, -1, :, :] & (1 << 0))
    else:
        assert np.all(fits_input['GROUPDQ'].data[:, -1, :, :]
                      == fits_output['GROUPDQ'].data[:, -1, :, :])