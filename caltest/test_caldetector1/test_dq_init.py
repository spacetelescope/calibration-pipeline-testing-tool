import numpy as np
import pytest
from jwst.dq_init import DQInitStep
from jwst import datamodels
from astropy.io import fits

@pytest.fixture(scope='module')
def output_model(input_model):
    return datamodels.open(input_model.meta.filename.replace('uncal', 'dqinitstep'))

def test_dq_init_step(input_model):
    DQInitStep.call(input_model, save_results=True)

def test_groupdq_initialization(output_model):
    assert np.all(output_model.groupdq == 0)

def test_err_initialization(output_model):
    assert np.all(output_model.err == 0)

def test_dq_def_initialization(output_model):
    assert hasattr(output_model, 'dq_def')