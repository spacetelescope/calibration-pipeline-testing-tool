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
    """
    Calculate the second difference of the linearity corrected ramp for each 
    pixel. If the ramp is perfectly linear they should be zero.
    """

    nints, ngroups, nx, ny = fits_output['SCI'].data.shape
    data_by_pixel = fits_output['SCI'].data.reshape(nints, ngroups, nx * ny)
    groupdq_by_pixel = fits_output['GROUPDQ'].data.reshape(nints, ngroups,
                                                           nx * ny)
    masked_output = np.ma.array(data_by_pixel, mask=groupdq_by_pixel.astype(bool))
    masked_input = np.ma.array(fits_input['SCI'].data.reshape(nints, ngroups, nx * ny),
                               mask=groupdq_by_pixel.astype(bool))
    second_diff = np.ma.diff(masked_output, n=2, axis=1)

    # make plot
    base = fits_input[0].header['FILENAME'].split('.')[0]
    plot_fname = 'test_linearity_residuals_'+base+'.pdf'
    plt.clf()
    plt.plot(masked_input.data[0, 1:-1, :].flatten(),
             second_diff.data[0, :, :].flatten(), ',k', alpha=.01)
    plt.ylim(-250, 250)
    plt.ylabel('Second Difference')
    plt.xlabel('Uncorrected Counts (DN)')
    plt.savefig(plot_fname)
