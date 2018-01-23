from ..utils import translate_dq

import numpy as np
import pytest
from jwst.dq_init import DQInitStep
from astropy.io import fits
import os

@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = fits_input['PRIMARY'].header['filename'].replace('.fits',
                                                             '_dqinitstep.fits')
    yield fits.open(fname)
    os.remove(fname)

@pytest.fixture(scope='module')
def fits_mask(fits_output):
    ref_path = fits_output['PRIMARY'].header['R_MASK']
    ref_path = ref_path.replace('crds://', '/grp/crds/cache/references/jwst/')
    return fits.open(ref_path)

def test_dq_init_step(fits_input):
    """Make sure the DQInitStep runs without error."""
    fname = fits_input['PRIMARY'].header['filename'].replace('.fits',
                                                             '_dqinitstep.fits')
    DQInitStep.call(fits_input, output_file=fname, save_results=True)

def test_pixeldq_initialization(fits_output, fits_mask):
    np.all(fits_output['PIXELDQ'].data == translate_dq(fits_mask))

def test_groupdq_initialization(fits_output):
    """
    Check that the GROUPDQ extension is added to the data and all 
    values are initialized to zero.	
    """
    assert 'GROUPDQ' in fits_output
    assert np.all(fits_output['GROUPDQ'].data == 0)

def test_err_initialization(fits_output):
    """Check that the error array is a 4-D array initialized to zero."""
    assert 'ERR' in fits_output
    assert fits_output['ERR'].data.ndim == 4
    assert np.all(fits_output['ERR'].data == 0)

# def test_dq_def_initialization(fits_output):
#     """
#     Check that a DQ_DEF extension with the definition of DQ flags is present.
#     """
#     assert 'DQ_DEF' in fits_output