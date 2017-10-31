from ..utils import translate_dq, extract_subarray

import os
import numpy as np
import pytest
from astropy.io import fits
from jwst.superbias import SuperBiasStep
from jwst import datamodels
import numpy as np
from scipy.stats import normaltest
from astropy.stats import sigma_clipped_stats
import matplotlib.pyplot as plt

@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_superbiasstep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    os.remove(fname)

@pytest.fixture(scope='module')
def fits_superbias(fits_output):
    ref_path = fits_output['PRIMARY'].header['R_SUPERB']
    ref_path = ref_path.replace('crds://', '/grp/crds/cache/references/jwst/')
    return fits.open(ref_path)

def test_superbias_step(fits_input):
    """Make sure the DQInitStep runs without error."""

    SuperBiasStep.call(datamodels.open(fits_input), save_results=True)

def test_superbias_subtraction(fits_input, fits_output, fits_superbias):

    if fits_input[0].header['SUBARRAY'] == fits_superbias[0].header['SUBARRAY']:
        bias = fits_superbias['SCI'].data
    else:
        bias = extract_subarray(fits_superbias['SCI'].data, fits_input)

    bias_to_subtract = np.copy(bias)
    bias_to_subtract[np.isnan(bias_to_subtract)] = 0

    assert np.allclose(fits_output['SCI'].data, (fits_input['SCI'].data - bias_to_subtract))

def test_superbias_residuals(fits_output, fits_input):

    mean, median, std = sigma_clipped_stats(fits_output['SCI'].data[0,0,:,:],
                                            fits_output['PIXELDQ'].data.astype(bool),
                                            iters=None)

    print("Sigma clipped stats")
    print("mean = {}".format(mean))
    print("median = {}".format(median))
    print("standard deviation = {}".format(std))

    # normaltest(fits_output['SCI'].data)
    # make plot
    base = fits_input[0].header['FILENAME'].split('.')[0]
    plot_fname = 'test_superbias_residuals_'+base+'.png'
    plt.clf()
    plt.hist(fits_output['SCI'].data[0,0,:,:].flatten(),
             range=(median - 5 * std, median + 5 * std),
             bins=100)
    plt.savefig(plot_fname)


def test_pixeldq_propagation(fits_input, fits_output, fits_superbias):
    # translate dq flags to standard bits
    pixeldq = translate_dq(fits_superbias)
    # extract subarray
    pixeldq = extract_subarray(pixeldq, fits_input)

    assert np.all(fits_output['PIXELDQ'].data == np.bitwise_or(fits_input['PIXELDQ'].data, pixeldq))

