from ..utils import translate_dq, extract_subarray

import os
import numpy as np
import pytest
from astropy.io import fits
from jwst.superbias import SuperBiasStep
from jwst import datamodels


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

    bias = extract_subarray(fits_superbias['SCI'].data, fits_input)
    bias_to_subtract = np.copy(bias)
    bias_to_subtract[np.isnan(bias_to_subtract)] = 0

    assert np.allclose(fits_output['SCI'].data, (fits_input['SCI'].data - bias_to_subtract))

def test_pixeldq_propagation(fits_input, fits_output, fits_superbias):
    # translate dq flags to standard bits
    pixeldq = translate_dq(fits_superbias)
    # extract subarray
    pixeldq = extract_subarray(pixeldq, fits_input)

    assert np.all(fits_output['PIXELDQ'].data == np.bitwise_or(fits_input['PIXELDQ'].data, pixeldq))

