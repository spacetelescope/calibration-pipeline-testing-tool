import pytest
import numpy as np
from jwst.refpix import RefPixStep
from jwst import datamodels
from astropy.io import fits
from scipy.stats import sigmaclip
import matplotlib.pyplot as plt
import os
from ..utils import translate_dq, extract_subarray

@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_refpixstep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    # delete the output FITS file after this module is finished
    os.remove(fname)


def median_refpix(array, smoothing_length, pixel_dq):
    # This code computes the median reference pixel value in teh "use_side_ref_pix = True" option of the reference pixel correction.
    # array must be 2048x4


    # first pad array with reflect

    parray = np.pad(array,
                    ((smoothing_length // 2, smoothing_length // 2), (0, 0)),
                    'reflect')
    ppdq = np.pad(pixel_dq,
                  ((smoothing_length // 2, smoothing_length // 2), (0, 0)),
                  'constant', constant_values=0)
    xmin = smoothing_length
    xmax = 2048 + smoothing_length - 1

    med_arr = np.zeros(2048)

    for i in range(2048):
        sub_array = parray[
                    i + smoothing_length // 2 - smoothing_length // 2:i + smoothing_length // 2 + smoothing_length // 2 + 1,
                    :]
        sub_pdq = ppdq[
                  i + smoothing_length // 2 - smoothing_length // 2:i + smoothing_length // 2 + smoothing_length // 2 + 1,
                  :]
        good = np.where(sub_pdq != 1)
        med_arr[i] = np.median(sub_array[good])

    return (med_arr)

def test_refpix_step(fits_input):
    """Make sure the DQInitStep runs without error."""

    RefPixStep.call(datamodels.open(fits_input), save_results=True)

@pytest.mark.parametrize("odd_even_columns", [True, False])
@pytest.mark.parametrize("use_side_ref_pixels", [True, False])
def test_refpix_correction(fits_input, fits_output, odd_even_columns, use_side_ref_pixels):
    """
    Test for the reference pixel correction
    INPUTS:
         "input_files", A list of input files (files that were input in the pipeline step
         "ouput_files", A list of output files (files that were output by the pipeline step)
         "input_files", "output_files" must have the same length
         "test_key": A string to identify the text file written by the step, which contains the min/max/median/mean differences
    OPTIONAL PARAMETERS:
         Same as those used in the reference pixel correction
    OUTPUTS:
         NONE
         This step will write a text file ('refpix_testing_results' +... + '.dat') containing some stats on the differences found. "..." stands for suffixes reflecting which optinoal paramaeters were used.
         This step will also write fits files (input_files + '_refpix_dif_val.fits', '_refpix_exp_out.fits', 'refpix_means.fits') with 1) the fractional difference (pipeline-mine)/mine), 2) my output, 3) the 1D means array
    """
    side_smoothing_length = 11
    side_gain = 1.

    delta_amp = 512
    if odd_even_columns==False:
        xs=[np.arange(delta_amp, dtype = 'uint32')]
    else:
        xs=[np.arange(delta_amp//2, dtype='uint32')*2, np.arange(delta_amp//2, dtype = 'uint32')*2 + 1]

    data_in = fits_input
    data_out = fits_output

    subarray = data_in[0].header['SUBARRAY']

    if subarray == 'FULL':
        sci_in = data_in[1].data
        sci_out = data_out[1].data

        # dif_in_out = sci_out - sci_in
        # file = input_files[i]
        # dif_file = file.replace(".fits",
        #                         "refpix_dif_int-out" + oe_key + skey + ".fits")
        # dif_hdu = fits.PrimaryHDU(dif_in_out)
        # hdulist = fits.HDUList([dif_hdu])
        # hdulist.writeto(dif_file, clobber=True)

        gdq_in = data_in[3].data
        pdq_in = data_in[2].data


        sci_shape = sci_in.shape
        niter = sci_shape[0]
        ngroup = sci_shape[1]

        fsci_in = np.swapaxes(sci_in, 2, 3)[:, :, ::-1, ::-1]
        fsci_out = np.swapaxes(sci_out, 2, 3)[:, :, ::-1, ::-1]

        fgdq_in = np.swapaxes(gdq_in, 2, 3)[:, :, ::-1, ::-1]
        fpdq_in = np.swapaxes(pdq_in, 0, 1)[::-1, ::-1]


        fpdq_rep = np.array([fpdq_in, ] * ngroup)

        fsci_shape = fsci_in.shape

        fexp_sci_out = np.zeros(fsci_shape, dtype='float32')

        if odd_even_columns == True:
            top_means = np.zeros([niter, ngroup, 4, 2], dtype='float32')
            bottom_means = np.zeros([niter, ngroup, 4, 2], dtype='float32')
            means = np.zeros([niter, ngroup, 4, 2], dtype='float32')

        else:
            top_means = np.zeros([niter, ngroup, 4, 1], dtype='float32')
            bottom_means = np.zeros([niter, ngroup, 4, 1], dtype='float32')
            means = np.zeros([niter, ngroup, 4, 1], dtype='float32')

        for it in range(niter):
            subg_fsci_in = fsci_in[it, :, :, :]
            subm_fsci_in = subg_fsci_in.copy()

            for ig in range(ngroup):
                for ia in range(4):

                    zerox = ia * delta_amp

                    for io in range(len(xs)):
                        sub_pdq_top = fpdq_rep[ig, 2044:2048, zerox + xs[io]]
                        sub_gdq_top = fgdq_in[it, ig, 2044:2048, zerox + xs[io]]
                        sub_sci_top = subg_fsci_in[ig, 2044:2048,
                                      zerox + xs[io]]

                        sub_pdq_bottom = fpdq_rep[ig, 0:4, zerox + xs[io]]
                        sub_gdq_bottom = fgdq_in[it, 0:4, ig, zerox + xs[io]]
                        sub_sci_bottom = subg_fsci_in[ig, 0:4, zerox + xs[io]]

                        valid_top = np.where(
                            (sub_pdq_top != 1) & (sub_gdq_top != 1))
                        valid_bottom = np.where(
                            (sub_pdq_bottom != 1) & (sub_gdq_bottom != 1))

                        # top_means[it, ig,ia, io] = np.mean(sigma_clip(sub_sci_top[valid_top]))
                        # bottom_means[it, ig, ia,io] = np.mean(sigma_clip(sub_sci_bottom[valid_bottom]))
                        top_means[it, ig, ia, io] = np.mean(
                            sigmaclip(sub_sci_top[valid_top], low=3.0,
                                      high=3.0).clipped)
                        bottom_means[it, ig, ia, io] = np.mean(
                            sigmaclip(sub_sci_bottom[valid_bottom], low=3.0,
                                      high=3.0).clipped)
                        means[it, ig, ia, io] = (top_means[it, ig, ia, io] +
                                                 bottom_means[
                                                     it, ig, ia, io]) / 2.

                        subm_fsci_in[ig, :, zerox + xs[io]] = subg_fsci_in[ig,
                                                              :,
                                                              zerox + xs[io]] - \
                                                              means[
                                                                  it, ig, ia, io]

                if use_side_ref_pixels == True:
                    sub_pdq_left = fpdq_rep[ig, :, 0:4]
                    sub_sci_left = subm_fsci_in[ig, :, 0:4]
                    sub_pdq_right = fpdq_rep[ig, :, 2044:2048]
                    sub_sci_right = subm_fsci_in[ig, :, 2044:2048]

                    left_means = median_refpix(sub_sci_left,
                                               side_smoothing_length,
                                               sub_pdq_left)
                    right_means = median_refpix(sub_sci_right,
                                                side_smoothing_length,
                                                sub_pdq_right)

                    lr_means = 0.5 * (left_means + right_means) * side_gain

                    mrep = np.array([lr_means, ] * 2048)
                    mrep = np.swapaxes(mrep, 0, 1)

                    subm_fsci_in[ig, :, :] = subm_fsci_in[ig, :, :] - mrep

            fexp_sci_out[it, :, :, :] = subm_fsci_in

        exp_sci_out = np.swapaxes(fexp_sci_out, 2, 3)[:, :, ::-1, ::-1]

        assert np.allclose(sci_out, exp_sci_out)

