from ..utils import extract_subarray, translate_dq

import os
import numpy as np
import pytest
from astropy.io import fits
from jwst.saturation import SaturationStep
from jwst import datamodels


@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_saturationstep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    os.remove(fname)

@pytest.fixture(scope='module')
def fits_saturation(fits_output):
    ref_path = fits_output['PRIMARY'].header['R_SATURA']
    ref_path = ref_path.replace('crds://', '/grp/crds/cache/references/jwst/')
    return fits.open(ref_path)

def test_saturation_step(fits_input):
    """Make sure the DQInitStep runs without error."""

    SaturationStep.call(datamodels.open(fits_input), save_results=True)

def test_groupdq_flagging(fits_output, fits_saturation):

    satmask = extract_subarray(fits_saturation['SCI'].data, fits_output)
    dqmask = translate_dq(fits_saturation)
    dqmask = extract_subarray(dqmask, fits_output)
    # flag pixels greater than saturation threshold
    no_sat_check = (dqmask & (1 << 21)).astype(bool)
    not_nan = ~np.isnan(satmask)
    expected_groupdq = np.zeros_like(fits_output['GROUPDQ'].data)
    flagged = (fits_output['SCI'].data >= satmask) & ~no_sat_check[np.newaxis, np.newaxis, :, :] & not_nan[np.newaxis, np.newaxis, :, :]
    expected_groupdq[flagged] = 2

    # make sure that pixels in groups after a flagged pixel are also flagged
    flagged = np.cumsum(expected_groupdq == 2, axis=1) > 0
    expected_groupdq[flagged] = 2

    assert np.all(fits_output['GROUPDQ'].data == expected_groupdq)
