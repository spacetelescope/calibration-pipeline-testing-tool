#! /usr/bin/env python

'''
Test the persistence step of the pipeline. Written during 
testing of build 7.1

Validation Part 1:
Check that trapsfilled file is generated correctly
Check that it’s (the step?) used correctly


SSB documentation:
Based on a model, this step computes the number of traps 
that are expected to have captured or released a charge 
during an exposure. The released charge is proportional 
to the persistence signal, and this will be subtracted 
(group by group) from the science data. An image of the 
number of filled traps at the end of the exposure will 
be written as an output file, in order to be used as input 
for correcting the persistence of a subsequent exposure.

Input
The input science file is a RampModel.

A trapsfilled file (TrapsFilledModel) may optionally be 
passed as input as well. This normally would be specified 
unless the previous exposure with the current detector was 
taken more than several hours previously, that is, so long 
ago that persistence from that exposure could be ignored.

Output
The output science file is a RampModel, a persistence-corrected 
copy of the input data.

A second output file will be written, with suffix “_trapsfilled”. 
This is a TrapsFilledModel, the number of filled traps at each 
pixel at the end of the exposure. This takes into account the 
capture of charge by traps due to the current science exposure, 
as well as the release of charge from traps shown in the input 
trapsfilled file, if one was specified.

If the user specified save_persistence=True, a third output file 
will be written, with suffix “_output_pers”. This is a RampModel 
matching the output science file, but this gives the persistence 
that was subtracted from each group in each integration.

input file -> run persistence step -> output hdu and file -> 
run tests against...what truth?

'''

import pytest
import os
import numpy as np
from astropy.io import fits
from jwst import datamodels
from jwst.persistence import PersistenceStep
#from jwst.datamodels import TrapsFilledModel
from jwst.datamodels import dqflags


#@pytest.fixture(scope="module")
#def input_hdul(request, config):
#    if  config.has_option("persistence", "input_file"):
#        curdir = os.getcwd()
#        config_dir = os.path.dirname(request.config.getoption("--config_file"))
#        os.chdir(config_dir)
#        hdul = fits.open(config.get("persistence", "input_file"))
#        os.chdir(curdir)
#        return hdul
#    else:
#       pytest.skip("needs persistence input_file")

        
@pytest.fixture(scope="module")
def out_hdul(fits_input):
    fname = '_persist.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    #os.remove(fname)


@pytest.fixture(scope="module")
def trapsfilled_hdul(trapsfilled):
    yield fits.open(trapsfilled)


@pytest.fixture(scope='module')
def traps_hdul(fits_input):
    fname = '_trapsfilled.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    #os.remove(fname)


@pytest.fixture(scope='module')
def pers_hdul(fits_input):
    fname = '_output_pers.'.join(fits_input[0].header['filename'].split('.'))
    try:
        hdul = fits.open(fname)
    except:
        print("output_pers file not present")
        hdul = None    
    yield hdul
    #os.remove(fname)

    
@pytest.fixture(scope="module")
def persat_hdul(out_hdul):
    CRDS = '/grp/crds/cache/references/jwst/'
    ref_file = output_hdul[0].header['R_PERSAT']
    if 'crds://' in ref_file:
        ref_file = ref_file.replace('crds://',CRDS)
    return fits.open(ref_file)


@pytest.fixture(scope="module")
def trpden_hdul(output_hdul):
    CRDS = '/grp/crds/cache/references/jwst/'
    ref_file = output_hdul[0].header['R_TRPDEN']
    if 'crds://' in ref_file:
        ref_file = ref_file.replace('crds://',CRDS)
    return fits.open(ref_file)


@pytest.fixture(scope="module")
def trppar_hdul(output_hdul):
    CRDS = '/grp/crds/cache/references/jwst/'
    ref_file = output_hdul[0].header['R_TRPPAR']
    if 'crds://' in ref_file:
        ref_file = ref_file.replace('crds://',CRDS)
    return fits.open(ref_file)


def test_run_persist_step(fits_input,trapsfilled):
    outfile = fits_input[0].header['FILENAME'].replace('.fits','_persist.fits')
    if trapsfilled.lower() in ["none",""]:
        PersistenceStep.call(fits_input,save_persistence=True,\
                             output_file=outfile,save_results=True)
    else:
        PersistenceStep.call(fits_input,save_persistence=True,\
                             output_file=outfile,save_results=True,\
                             input_trapsfilled=trapsfilled)


def test_persistence_trapsfilled_shape(fits_input,traps_hdul,trapsfilled):
    '''Check to see that the OUPUT trapsfilled
    file was created.'''
    x,y = fits_input['SCI'].data.shape[-2:]
    print("Science data shape (x,y) = ({},{})".format(x,y))
    assert traps_hdul['SCI'].data.shape == (3,y,x)

    
def test_persistence_output_pers_shape(fits_input,pers_hdul,trapsfilled):
    '''Check that the optional output file
    "_output_pers.fits" was created if
    the save_persistence option in the persistence
    step was set to True. (Assume this test will
    only be called in instances when save_persistence
    is True'''
    opshape = pers_hdul['SCI'].data.shape
    print("Output_pers data shape: {}".format(opshape))
    assert opshape == fits_input['SCI'].data.shape


def test_persistence_subtracted_signal(fits_input, out_hdul, pers_hdul, trapsfilled):
    '''Check that the signal values contained in the 
    output_pers file are indeed subtracted from the original
    input file.'''
    assert np.allclose(out_hdul[1].data,fits_input[1].data - pers_hdul[1].data)


def test_persistence_dq_flagged_pix(out_hdul,pers_hdul,trapsfilled,flagthresh=40):
    '''Pixels that have more persistence signal than flag_pers_cutoff
    should be flagged in the DQ array of the output file. The default
    value of flag_pers_cutoff is 40 DN'''
    # Check only integration #1
    pdata = pers_hdul['SCI'].data[0,:,:,:]
    # Keep only the maximum persistence value
    # for each pixel
    if ((flagthresh is not None) and (flagthresh > 0)):
        collapsed = np.max(pdata,axis=0)
        flagged = collapsed > flagthresh
        dq_data = out_hdul['PIXELDQ'].data
        print(("{} pixels have persistence values above the threshold "
               "of {}.".format(np.sum(flagged),flagthresh)))
        assert np.all(dq_data[flagged] & dqflags.pixel['DO_NOT_USE'] > 0)
    else:
        print("Flagthresh is {}".format(flagthresh))
        assert True == True

        
#def test_calculated_persistence(fits_input,pers_hdul,persat_hdul,trapsfilled):
#    '''Using Regan's paper (JWST-STScI-005689), manually
#    calculate the expected amount of persistence in the input
#    file, and compare to the pipeline's calculations
#
#    Not sure how to do this without simply copying the
#    code in the jwst cal pipeline step.
#    '''

    #data = fits_input['SCI'].data[0,:,:,:]
    #f21 = data[1,:,:] = data[0,:,:]
    #fw_frac = f21 / persat_hdul['SCI']

    #trapc - total number of traps captured
    #trape - num of traps that fit exponential decay (?)
    #tau - time constant of capture
    #trapi - num traps instantaneously captured
    #S - rate of change in the depletion region in units of fraction of full
    #    well per unit time
    #T - integration time

    #trapc = s*(T*(trape + trapi) + trape*tau*(exp(-T/tau) - 1))
