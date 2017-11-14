import pytest
import numpy as np
from jwst.dark_current import DarkCurrentStep
from jwst import datamodels
from astropy.io import fits
import matplotlib.pyplot as plt
import os
from ..utils import translate_dq, extract_subarray


@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_darkcurrentstep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    # delete the output FITS file after this module is finished
    os.remove(fname)

@pytest.fixture(scope='module')
def fits_dark(fits_output):
    ref_path = fits_output['PRIMARY'].header['R_DARK']
    ref_path = ref_path.replace('crds://', '/grp/crds/cache/references/jwst/')
    return fits.open(ref_path)

def test_dark_current_step(fits_input):
    """Make sure the DQInitStep runs without error."""

    DarkCurrentStep.call(datamodels.open(fits_input), save_results=True)

def test_dark_subtraction(fits_input, fits_dark, fits_output):
    nframes = fits_output[0].header['NFRAMES']
    groupgap = fits_output[0].header['GROUPGAP']
    nints, ngroups, nx, ny = fits_output['SCI'].shape
    nframes_tot = (nframes + groupgap) * ngroups
    if nframes_tot > fits_dark['SCI'].data.shape[0]:
        # data should remain unchanged if there are more frames in the
        # science data than the reference file
        assert np.all(fits_input['SCI'].data == fits_output['SCI'].data)

    else:
        dark_correct = np.zeros((nframes, ngroups, nx, ny))
        data = fits_dark['SCI'].data[:nframes_tot, :, :]
        for i in range(nframes):
            dark_correct[i] = data[i::(nframes + groupgap), :, :]

        dark_correct = np.average(dark_correct, axis=0)
        dark_correct[np.isnan(dark_correct)] = 0
        result = fits_input['SCI'].data - dark_correct
        assert np.allclose(result, fits_output['SCI'].data)


def test_dark_current_quality(fits_input, fits_output):
    """
    Check the slope of the median ramp for the detector.  The count rate of the
    dark subtracted ramp should be small (< 0.1?)
    
    :param fits_input: astropy.io.fits.HDUList
        The FITS HDUList input
    :param fits_output: astropy.io.fits.HDUList
        The FITS HDUList output
    """
    med_in = np.median(fits_input['SCI'].data[0, :, :, :], axis=(1, 2))
    med_out = np.median(fits_output['SCI'].data[0, :, :, :,], axis=(1,2))
    groups = np.arange(med_in.shape[0])

    slope_in, _ = np.polyfit(groups, med_in, 1)
    slope_out, _ = np.polyfit(groups, med_out, 1)

    print(
    "Slope of median ramp before dark subtraction: {} counts/group".format(
        slope_in))
    print(
    "Slope of median ramp after dark subtraction: {} counts/group".format(
        slope_out))

    plt.clf()
    plt.plot(med_in, label='input')
    plt.plot(med_out, label='output')
    base = fits_input[0].header['FILENAME'].split('.')[0]
    plot_fname = 'test_dark_current_quality_'+base+'.pdf'
    plt.xlabel('Group Number')
    plt.ylabel('Counts')
    plt.savefig(plot_fname)

    assert abs(slope_out) < 0.1

def test_pixeldq_propagation(fits_input, fits_output, fits_dark):

    # translate dq flags to standard bits
    pixeldq = translate_dq(fits_dark)
    # extract subarray
    if fits_dark[0].header['SUBARRAY'] == 'GENERIC':
        pixeldq = extract_subarray(pixeldq, fits_input)

    assert np.all(fits_output['PIXELDQ'].data == np.bitwise_or(fits_input['PIXELDQ'].data, pixeldq))
