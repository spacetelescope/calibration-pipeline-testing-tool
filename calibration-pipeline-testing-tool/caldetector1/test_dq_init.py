import numpy as np


def test_dq_init_step(request, input_model):
    request.config.model = DQInitStep.call(input_model)

def test_groupdq_initialization(output_model):
    assert np.all(output_model.groupdq == 0)

def test_err_initialization(output_model):
    assert np.all(output_model.err == 0)

def test_dq_def_initialization(output_model):
    assert hasattr(output_model, 'dq_def')