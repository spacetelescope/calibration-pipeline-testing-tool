from ..utils import translate_dq, extract_subarray

import os
import numpy as np
import pytest
from astropy.io import fits
from jwst.linearity import LinearityStep
from jwst import datamodels
import matplotlib.pyplot as plt
import os

@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_linearitystep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    os.remove(fname)

@pytest.fixture(scope='module')
def fits_linearity(fits_output):
    ref_path = fits_output['PRIMARY'].header['R_LINEAR']
    ref_path = ref_path.replace('crds://', '/grp/crds/cache/references/jwst/')
    return fits.open(ref_path)

def test_linearity_step(fits_input):
    """Make sure the LinearityStep runs without error."""

    LinearityStep.call(datamodels.open(fits_input), save_results=True)

def extract_coeffs(coeffs, hdul):
    xsize = hdul['PRIMARY'].header['SUBSIZE1']
    xstart = hdul['PRIMARY'].header['SUBSTRT1']
    ysize = hdul['PRIMARY'].header['SUBSIZE2']
    ystart = hdul['PRIMARY'].header['SUBSTRT2']
    return coeffs[::-1, ystart - 1:ysize + ystart - 1,
                  xstart - 1:xstart + xsize - 1]

def test_linearity_correction(fits_input, fits_linearity, fits_output):
    """
    Check that the linearity correction is properly applied to all relevant pixels. The algorithm
    uses a polynomial of the form
    .. math::
        F_c = \sum_{i=0}^N C_i F^i

    where :math:`F_c` is the corrected counts, :math:`C` are the correction coefficients, and :math:`F`
    is the uncorrected counts.  The coefficients of the polynomial at each pixel are given by the
    reference file.
    """

    # # ignore pixels which are saturated (GROUPDQ = 2) or NO_LIN_CORR (DQ = 2)
    no_lin_corr = (translate_dq(fits_linearity) & (1 << 20)).astype(bool)
    no_lin_corr = extract_subarray(no_lin_corr, fits_input)
    saturated = (fits_input['GROUPDQ'].data & (1 << 2)).astype(bool)
    needs_correction = np.logical_not(np.logical_or(saturated, no_lin_corr))

    linearity_applied = np.allclose(
        np.polyval(extract_coeffs(fits_linearity['COEFFS'].data,
                                  fits_input),
                   fits_input['SCI'].data)[needs_correction],
        fits_output['SCI'].data[needs_correction])

    linearity_ignored = np.allclose(fits_input['SCI'].data[~needs_correction],
                                    fits_output['SCI'].data[~needs_correction])

    # make sure that the values linearity correction is properly applied to relevant pixels
    # and ignored elsewhere
    assert linearity_applied and linearity_ignored

def test_pixeldq_propagation(fits_input, fits_output, fits_linearity):

    # translate dq flags to standard bits
    pixeldq = translate_dq(fits_linearity)
    # extract subarray
    pixeldq = extract_subarray(pixeldq, fits_input)

    assert np.all(fits_output['PIXELDQ'].data == np.bitwise_or(fits_input['PIXELDQ'].data, pixeldq))

def test_linearity_residuals(fits_input, fits_output):
    ints, groups, nx, ny = fits_output['SCI'].data.shape
    ramps = np.ma.array(fits_output['SCI'].data[0,:,:,:],
                        mask=fits_output['GROUPDQ'].data[0,:,:,:].astype(bool))
    ramps = ramps.reshape((groups, nx*ny))
    x = np.ma.array(np.arange(ramps.shape[0]), mask=ramps[:, 512*512].mask)
    p = np.ma.polyfit(x, ramps[:, 512*512], 1)
    val = np.polyval(p, x)

    # make plot
    base = fits_input[0].header['FILENAME'].split('.')[0]
    plot_fname = 'test_linearity_residuals_'+base+'.png'
    plt.plot(x, ramps[:, 512*512],'o')
    plt.plot(x, val)
    plt.savefig(plot_fname)
