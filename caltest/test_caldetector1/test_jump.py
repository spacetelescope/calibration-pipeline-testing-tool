import pytest
import numpy as np
from jwst.jump import JumpStep
from jwst import datamodels
from astropy.io import fits, ascii
from astropy.table import Table
import os

@pytest.fixture(scope='module')
def fits_output(fits_input):
    fname = '_jumpstep.'.join(fits_input[0].header['filename'].split('.'))
    yield fits.open(fname)
    # delete the output FITS file after this module is finished
    os.remove(fname)

def test_jump_step(fits_input):
    """Make sure the JumpStep runs without error."""

    JumpStep.call(datamodels.open(fits_input), save_results=True)


def test_jump_performance(fits_output, rejection_threshold=5.0,
                          do_yintercept=False, yint_threshold=1.0):
    # Test function for the jump correction. Type should be set to "cv3_dark" as in "run_jump_testing()". Output_file is the file output by the pipeline after the jump correction. Optional paramters are the same as for the jump correction.

    rej_key = str(rejection_threshold).strip()
    yint_key = str(yint_threshold).strip()
    if do_yintercept == True:
        doyint_key = '_doyint'
    else:
        doyint_key = ''

    # First read in the output file, get the GROUPDQ extension, and transform it from DMS to detector coordinates, because the images of CRs from the library and the CR position list from the simulations are in detector coordinates.
    # file = output_file

    data = fits_output
    gdq_out = data['GROUPDQ'].data
    gdq_out = np.swapaxes(gdq_out, 2, 3)[:, :, ::-1, ::-1]

    # Read in the list of CRs injected in the simulation

    cr_list = ascii.read("/grp/jwst/ins/calibration-pipeline-testing-tool/test_data/jump/NIRISS/cosmicrays.list")
    # CR coordinates, amplitude, set and sample (from hte library) from which they are extracted.
    cr_x = np.array(cr_list['x'])
    cr_y = np.array(cr_list['y'])
    cr_z = np.array(cr_list['z'])
    cr_ampl = np.array(cr_list['amplitude'])
    cr_set = np.array(cr_list['set'])
    cr_sample = np.array(cr_list['sample'])
    nset = np.max(cr_set) + 1
    ncr = cr_x.shape[0]

    # binary decomp of GDQ array, useful to tell whether or not the jump flag is set.
    # binary, powers = binary_decomp(gdq_out,
    #                                gdq=True)  # array that is size ( it, ig, ny, ny, 32)

    # just get the jump bit
    # print("BIN DECOMP ", binary.shape, powers.shape)
    binary_jump = (fits_output['GROUPDQ'].data & (1 << 1)).astype(bool).astype('uint32')[0, :, :, :]
    print("TRUNC BIN ", binary_jump.shape)

    # Create an zero array that will contain where the jump flags should be
    exp_binary_jump = np.zeros(binary_jump.shape, dtype='uint32')

    # create the array that will contain the amplitudes of the jumps
    jump_values = np.zeros(binary_jump.shape, dtype='float32')

    # BElow:
    # check that all CR in list are detected in GDQ
    # check that all CR detected in GDQ are in the list

    print(exp_binary_jump.shape)

    # Loop over the sets because the CR images from the library take a long time to open. So open each set, then loop over all CRs in that set

    for iset in range(nset):
        cr_image = fits.open(
            "/grp/jwst/nis1/JRD/rampsim/CR_lib/CRs_MCD5.5_SUNMIN_0" + str(
                iset).strip() + "_IPC.fits")
        cr_image = cr_image[1].data

        # identify all teh CRs in teh list that were from this set
        index = np.where(cr_set == iset)
        index = index[0]
        ncr_set = index.shape[0]

        # for each cosmic ray in that set
        for i in range(ncr_set):
            ind = index[i]
            xi = cr_x[ind] - 1
            yi = cr_y[ind] - 1
            zi = cr_z[ind] - 1
            si = cr_sample[ind] - 1

            # check size of affected area. A CR has a halo around it because of IPC correction. Identify pixels around the main CR that are not zero.

            this_image = cr_image[si, :, :]
            shapim = this_image.shape
            nx = shapim[1]
            ny = shapim[0]
            affected = np.where(this_image != 0)
            xaffected = affected[1] - nx // 2 + xi
            yaffected = affected[0] - ny // 2 + yi

            valid = np.where(
                (xaffected >= 0) & (xaffected < 2048) & (yaffected >= 0) & (
                yaffected < 2048))

            # all teh non-zero values in the CR image should be flagged by the pipeline, ideally, so the "expected" GDQ should have 1 in those pixels.
            exp_binary_jump[zi, yaffected[valid], xaffected[valid]] = 1

            # REcord the amplitudes of the CRs
            jump_values[zi, yaffected[valid], xaffected[valid]] = \
            jump_values[zi, yaffected[valid], xaffected[valid]] + \
            this_image[affected[0][valid], affected[1][valid]] / 1.61

    # compute the difference between the jump flags derived from the known CR coordinates injected in teh simulations and the flags found by the pipeline
    dif = exp_binary_jump - binary_jump

    min = np.min(dif)
    max = np.max(dif)

    # dif_file = file.replace(".fits", "jump_dif_" + type + ".fits")
    # dif_hdu = fits.PrimaryHDU(dif)
    # hdulist = fits.HDUList([dif_hdu])
    # hdulist.writeto(dif_file, clobber=True)
    #
    # gdq_file = file.replace(".fits", "jump_bgdq_" + type + ".fits")
    # exp_hdu = fits.PrimaryHDU(exp_binary_jump)
    # gdq_hdu = fits.ImageHDU(binary_jump)
    # hdulist = fits.HDUList([exp_hdu, gdq_hdu])
    # hdulist.writeto(gdq_file, overwrite=True)
    #
    # val_file = file.replace(".fits", "jump_val_" + type + ".fits")
    # val_hdu = fits.PrimaryHDU(jump_values)
    # hdulist = fits.HDUList([val_hdu])
    # hdulist.writeto(val_file, clobber=True)

    results = Table({'min': [min], 'max': [max]},
                    names=['min', 'max'])
    print(results)
    # ascii.write(results,
    #             'one_ramp_' + type + '/jump_testing_results_' + type + "_" + rej_key + "_" + yint_key + doyint_key + '.dat')



    # Look into the jumps not detected or false positives
    bad = np.where(dif == 1)
    zbad = bad[0]
    ybad = bad[1]
    xbad = bad[2]

    nbad = len(xbad)

    closest_x = np.zeros(nbad, dtype='uint32')
    closest_y = np.zeros(nbad, dtype='uint32')
    closest_z = np.zeros(nbad, dtype='uint32')
    closest_set = np.zeros(nbad, dtype='uint32')
    closest_sample = np.zeros(nbad, dtype='uint32')
    closest_ampl = np.zeros(nbad, dtype='uint32')
    jump_val = np.zeros(nbad, dtype='float32')
    gdq_val = np.zeros(nbad, dtype='uint32')

    for i in range(nbad):
        # match a discrepant pixel/group to the closest CR in the simulations' list, record the coordinates, set sample, and amplitude.
        dist = np.sqrt((cr_x - xbad[i]) ** 2 + (cr_y - ybad[i]) ** 2 + (
        cr_z - zbad[i]) ** 2)
        closest = np.argmin(dist)
        # closest_xyz = np.unravel_index(closest)
        closest_z[i] = cr_z[closest]
        closest_y[i] = cr_y[closest]
        closest_x[i] = cr_x[closest]
        closest_set[i] = cr_set[closest]
        closest_sample[i] = cr_sample[closest]
        closest_ampl[i] = cr_ampl[closest]
        jump_val[i] = jump_values[zbad[i], ybad[i], xbad[i]]
        gdq_val[i] = gdq_out[0, zbad[i], ybad[i], xbad[i]]

    bad_set = Table(
        {'x': xbad, 'cl_x': closest_x, 'y': ybad, 'cl_y': closest_y, 'z': zbad,
         'cl_z': closest_z, 'jump_val': jump_val, 'gdq_val': gdq_val,
         'cl_set': closest_set, 'cl_sample': closest_sample,
         'cl_ampl': closest_ampl},
        names=['x', 'cl_x', 'y', 'cl_y', 'z', 'cl_z', 'jump_val', 'gdq_val',
               'cl_set', 'cl_sample', 'cl_ampl'])
    print(bad_set)
    # ascii.write(bad_set,
    #             'one_ramp_' + type + '/bad_sets_' + type + "_" + rej_key + "_" + yint_key + doyint_key + '.dat')
