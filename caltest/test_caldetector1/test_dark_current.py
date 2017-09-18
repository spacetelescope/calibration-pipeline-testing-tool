def test_dark_subtraction(fits_input, fits_dark, fits_output):
    nframes = output_hdul[0].header['NFRAMES']
    groupgap = output_hdul[0].header['GROUPGAP']
    nints, ngroups, nx, ny = output_hdul['SCI'].shape
    nframes_tot = (nframes + groupgap) * ngroups
    if nframes_tot > reference_hdul['SCI'].data.shape[0]:
        # data should remain unchanged if there are more frames in the
        # science data than the reference file
        result = np.all(input_hdul['SCI'].data == output_hdul['SCI'].data)
        return result
    else:
        dark_correct = np.zeros((nframes, ngroups, nx, ny))
        data = reference_hdul['SCI'].data[:nframes_tot, :, :]
        for i in range(nframes):
            dark_correct[i] = data[i::(nframes + groupgap), :, :]

        dark_correct = np.average(dark_correct, axis=0)
        result = input_hdul['SCI'].data - dark_correct
        result = np.allclose(result, output_hdul['SCI'].data)
        return result
