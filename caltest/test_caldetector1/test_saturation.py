import numpy as np
from astropy.io import fits
from jwst.saturation import SaturationStep

@pytest.fixture(scope='module')
def fits_output(fits_input):
    yield fits.open(fits_input[0].header['filename'].replace('dqinitstep', 'saturationstep'))
    os.remove(fits_input[0].header['filename'].replace('dqinitstep', 'saturationstep'))

@pytest.fixture(scope='module')
def fits_saturation(fits_output):
    ref_path = fits_output['PRIMARY'].header['R_SATURA']
    ref_path = ref_path.replace('crds://', '/grp/crds/cache/references/jwst/')
    return fits.open(ref_path)

def test_dq_init_step(fits_input):
    """Make sure the DQInitStep runs without error."""
    SaturationStep.call(fits_input, save_results=True)

def test_groupdq_flagging(fits_output, fits_saturation):

    # extract subarray
    if fits_saturation['PRIMARY'].header['SUBARRAY'] == 'GENERIC':
        xsize = fits_output['PRIMARY'].header['SUBSIZE1']
        xstart = fits_output['PRIMARY'].header['SUBSTRT1']
        ysize = fits_output['PRIMARY'].header['SUBSIZE2']
        ystart = fits_output['PRIMARY'].header['SUBSTRT2']
        satmask = fits_saturation['SCI'].data[ystart - 1:ysize + ystart - 1,
                  xstart - 1:xstart + xsize - 1]

    else:
        satmask = fits_reffile['SCI'].data

    # flag pixels greater than saturation threshold
    expected_groupdq = np.zeros_like(fits_output['GROUPDQ'])
    flagged = fits_output['GROUPDQ'].data >= satmask
    expected_groupdq[flagged] = 2

    # make sure that pixels in groups after a flagged pixel are also flagged
    flagged = np.cumsum(expected_groupdq == 2, axis=1) > 0
    expected_groupdq[flagged] = 2

    assert np.all(fits_output['GROUPDQ'] == expected_groupdq)
