import pytest
import numpy as np
from jwst.dark_current import DarkCurrentStep
from jwst import datamodels
from astropy.io import fits
import os

@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_darkcurrentstep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
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
