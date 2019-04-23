def plot_coronal_test(seg_file, bmode_file, capsule_file, mask_file, lesion_slice_index, bmode_window, bmode_min_level, capsule_window,
                 capsule_min_level, swei_flag, outline_flag, slice_type, ax, fig):
    import matplotlib.pyplot as plt
    import nibabel as nib
    import nrrd
    import numpy as np

    seg_total = nrrd.read(seg_file)
    bmode_total = nib.load(bmode_file)
    capsule_total = nib.load(capsule_file)
    mask_total = nib.load(mask_file)

    mask_data = mask_total.dataobj[..., :]
    bmode_data = bmode_total.get_data()
    capsule_data = capsule_total.dataobj[..., :]
    seg_data = seg_total[0]
    seg_meta = seg_total[1]

    seg_offset_string = seg_meta['Segmentation_ReferenceImageExtentOffset']
    seg_voxel_scale = seg_meta['space directions']
    seg_offset = [int(i) for i in seg_offset_string.split()]

    bmode_data_slice = np.flipud(bmode_data[:, lesion_slice_index, :, 0].transpose())
    capsule_data_slice = np.flipud(capsule_data[:, lesion_slice_index, :].transpose())
    mask_data_slice = np.flipud(np.squeeze(mask_data[:, lesion_slice_index, :].transpose()))
    seg_data_slice = np.flipud(seg_data[:, lesion_slice_index - seg_offset[1], :].transpose())

    bmode_voxel_size = {'lat': bmode_total.get_qform()[2, 2]}
    bmode_lat = [z * bmode_voxel_size['lat'] for z in range(0, bmode_data.shape[2])]
    bmode_lat -= max(bmode_lat) / 2

    bmode_voxel_size['depth'] = bmode_total.get_qform()[0, 0]
    bmode_voxel_size['ele'] = bmode_total.get_qform()[1, 1]
    bmode_depth = [x * bmode_voxel_size['depth'] for x in range(0, bmode_data_slice.shape[0])]
    bmode_ele = [y * bmode_voxel_size['ele'] for y in range(0, bmode_data_slice.shape[1])]
    bmode_ele -= max(bmode_ele) / 2

    seg_voxel_size = {'lat': sum(seg_voxel_scale[0]), 'axial': abs(sum(seg_voxel_scale[1])),
                      'ele': abs(sum(seg_voxel_scale[2]))}
    seg_ele = [y * seg_voxel_size['ele'] for y in range(0, seg_data.shape[1])]
    seg_ele -= max(seg_ele) / 2

    xlim = int(bmode_data_slice.shape[0])
    ylim = int(bmode_data_slice.shape[1])

    seg_binary = np.zeros((xlim, ylim))
    for x in range(0, seg_data_slice.shape[0] - 1):
        for y in range(0, seg_data_slice.shape[1] - 1):
            seg_binary[x + seg_offset[1]][y + seg_offset[0]] = 1 * seg_data_slice[x][y]

    seg_binary_inv = 1 - seg_binary

    bmode_filtered = seg_binary_inv * bmode_data_slice
    capsule_filtered = seg_binary * capsule_data_slice
    capsule_filtered[capsule_filtered == 0] = np.NaN

    ax.imshow(bmode_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_depth), max(bmode_depth)], cmap='gray',
              vmin=bmode_min_level, vmax=bmode_min_level + bmode_window)
    if swei_flag == 0:
        ax.imshow(capsule_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_depth), max(bmode_depth)],
                  cmap='copper', vmin=capsule_min_level, vmax=capsule_min_level + capsule_window)
        ax.imshow(mask_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)],
                  cmap='winter')
        plt.title("ARFI Capsule/B-mode Background")

    else:
        cax = ax.imshow(capsule_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_depth), max(bmode_depth)],
                        cmap='inferno_r', vmin=capsule_min_level, vmax=capsule_min_level + capsule_window)
        plt.title("SWEI Capsule/B-mode Background")
        fig.colorbar(cax)

    ax.set_xlabel("Elevation (mm)")
    ax.set_ylabel("Depth (mm)")
