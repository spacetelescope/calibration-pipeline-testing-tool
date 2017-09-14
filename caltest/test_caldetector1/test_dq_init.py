import numpy as np
import pytest
from jwst.dq_init import DQInitStep
from jwst import datamodels
from astropy.io import fits
import os

@pytest.fixture(scope='module')
def output_model(input_model):
    yield datamodels.open(input_model.meta.filename.replace('uncal', 'dqinitstep'))
    os.remove(input_model.meta.filename.replace('uncal', 'dqinitstep'))

def test_dq_init_step(input_model):
    DQInitStep.call(input_model, save_results=True)

def test_groupdq_initialization(output_model):
    assert hasattr(output_model, 'groupdq')
    assert np.all(output_model.groupdq == 0)

def test_err_initialization(output_model):
    assert hasattr(output_model, 'err')
    assert output_model.err.ndim == 4
    assert np.all(output_model.err == 0)

def test_dq_def_initialization(output_model):
    assert hasattr(output_model, 'dq_def')