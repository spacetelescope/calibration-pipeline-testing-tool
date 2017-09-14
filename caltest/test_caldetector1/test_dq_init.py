import numpy as np
import pytest
from jwst.dq_init import DQInitStep
from astropy.io import fits
import os

@pytest.fixture(scope='module')
def fits_output(fits_input):
    yield fits.open(fits_input[0].header['filename'].replace('uncal', 'dqinitstep'))
    os.remove(fits_input[0].header['filename'].replace('uncal', 'dqinitstep'))

def test_dq_init_step(fits_input):
    """Make sure the DQInitStep runs without error."""
    DQInitStep.call(fits_input, save_results=True)

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

def test_dq_def_initialization(fits_output):
    """
    Check that a DQ_DEF extension with the definition of DQ flags is present.
    """
    assert 'DQ_DEF' in fits_output