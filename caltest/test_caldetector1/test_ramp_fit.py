import pytest
import numpy as np
from jwst.ramp_fitting import RampFitStep
from jwst import datamodels
from astropy.io import fits, ascii


@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_jumpstep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    # delete the output FITS file after this module is finished
    os.remove(fname)

def test_ramp_fit_step(fits_input):
    """Make sure the JumpStep runs without error."""

    RampFitStep.call(datamodels.open(fits_input), save_results=True)

def test_err_propagation(fits_output):
    """Check that values in ERR are the square root of 
    Poisson variance + Read Noise variance"""

    n_neg_poisson = np.sum(fits_output['VAR_POISSON'].data < 0)
    n_neg_total = np.sum(fits_output['VAR_POISSON'].data
                         + fits_output['VAR_RNOISE'].data
                         < 0)
    n_nan = np.sum(np.isnan(fits_output['ERR'].data))
    print("Number of pixels with negative possion variance: {}".format(n_neg_poisson))
    print("Number of pixels with negative total variance: {}".format(n_neg_total))
    print("Number of pixels with NaN error: {}".format(n_nan))

    assert np.allclose(fits_output['ERR'].data,
                       np.sqrt(fits_output['VAR_POISSON'].data
                               + fits_output['VAR_RNOISE'].data),
                       equal_nan=True)