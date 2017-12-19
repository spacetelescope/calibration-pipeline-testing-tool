import pytest
import numpy as np
from jwst.ramp_fitting import RampFitStep
from jwst import datamodels
from astropy.io import fits, ascii
from astropy.stats import sigma_clipped_stats
import os
import matplotlib.pyplot as plt

@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = fits_input[0].header['filename'].replace('.fits', '_rampfitstep.fits')
    yield fits.open(fname)
    # delete the output FITS file after this module is finished
    os.remove(fname)

@pytest.fixture(scope='module')
def fits_gain(fits_output):
    ref_path = fits_output['PRIMARY'].header['R_GAIN']
    ref_path = ref_path.replace('crds://', '/grp/crds/cache/references/jwst/')
    return fits.open(ref_path)

def test_ramp_fit_step(fits_input):
    """Make sure the RampFitStep runs without error."""
    fname = fits_input[0].header['filename'].replace('.fits', '_rampfitstep.fits')
    RampFitStep.call(datamodels.open(fits_input), output_file=fname, save_results=True)

def test_ramp_fit_slopes(fits_input, fits_output, fits_gain):
    """
    Check that output slope is close to the input slope is within 1-sigma of
    input slope.
    """
    _, med, stdev = sigma_clipped_stats((fits_output['SCI'].data * fits_gain['SCI'].data).flatten())

    print("Sigma-clipped median slope: {:.5f}".format(med))
    print("Sigma-clipped standard deviation of slope: {:.5f}".format(stdev))

    base = fits_input[0].header['FILENAME'].split('.')[0]
    plot_fname = 'test_ramp_fit_slopes_'+base+'.png'
    plt.clf()
    plt.xlabel("Output Slope (count/sec)")
    plt.hist((fits_output['SCI'].data * fits_gain['SCI'].data).flatten(),
         range=(0.5, 1.5), bins = 'auto', color = 'k')
    plt.savefig(plot_fname)

    assert med - stdev < 1 < med + stdev

def test_err_combination(fits_output):
    """
    Check that values in ERR are the square root of 
    Poisson variance + Read Noise variance
    """

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