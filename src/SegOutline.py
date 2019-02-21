def plot_combine(seg_file, bmode_file, capsule_file, mask_file, lesion_slice_index, bmode_window, bmode_min_level, capsule_window,
                 capsule_min_level, swei_flag, outline_flag, ax, fig):
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
     
    # Load B-mode file and split metadata from data
    bmode_voxel_size = {'lat': bmode_total.get_qform()[2, 2]}
    bmode_lat = [z*bmode_voxel_size['lat'] for z in range(0, bmode_data.shape[2])]
    bmode_lat -= max(bmode_lat) / 2
    bmode_slice_data = bmode_data[:, :, lesion_slice_index, 0]
    bmode_slice_data = bmode_slice_data.transpose()
    bmode_voxel_size['axial'] = bmode_total.get_qform()[0, 0]
    bmode_voxel_size['ele'] = bmode_total.get_qform()[1, 1]
    bmode_axial = [x*bmode_voxel_size['axial'] for x in range(0, bmode_slice_data.shape[0])]
    bmode_ele = [y*bmode_voxel_size['ele'] for y in range(0, bmode_slice_data.shape[1])]
    bmode_ele -= max(bmode_ele) / 2
    
    # Load ARFI file and split metadata from data
    capsule_data = capsule_data[:, :, lesion_slice_index]
    capsule_data = capsule_data.transpose()
    capsule_voxel_size = {'axial': capsule_total.get_qform()[0, 0], 'ele': capsule_total.get_qform()[1, 1]}
    capsule_ele = [y*capsule_voxel_size['ele'] for y in range(0, capsule_data.shape[1])]
    capsule_ele -= max(capsule_ele) / 2

    seg_binary = create_seg_layer(seg_total, bmode_slice_data, lesion_slice_index)
    seg_binary_inv = 1 - seg_binary

    capsule_filtered = seg_binary * capsule_data
    capsule_filtered[capsule_filtered == 0] = np.NaN
    bmode_filtered = create_outline(bmode_slice_data, seg_binary_inv, outline_flag)
    mask_filtered = create_mask_layer(mask_data, mask_total, lesion_slice_index, seg_binary)

    # Show the arrays on the same set of axes w/ different colormaps
    ax.imshow(bmode_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)], cmap='gray',
              vmin=bmode_min_level, vmax=bmode_min_level + bmode_window)
    if swei_flag == 0:
        ax.imshow(capsule_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)],
                            cmap='copper', vmin=capsule_min_level, vmax=capsule_min_level + capsule_window)
        ax.imshow(mask_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)],
                        cmap='winter')
        plt.title("ARFI Capsule/B-mode Background")
    else:
        cax = ax.imshow(capsule_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)],
                        cmap='inferno_r', vmin=capsule_min_level, vmax=capsule_min_level + capsule_window)
        plt.title("SWEI Capsule/B-mode Background")
        fig.colorbar(cax)
    
    # Add title, labels, and colorbar
    ax.set_xlabel("Elevation (mm)")
    ax.set_ylabel("Depth (mm)")


def check_neighbors(x_coordinate, y_coordinate, seg_binary_inverse):
    if seg_binary_inverse[x_coordinate][y_coordinate] != 0:
        x_delta = [0, 0, -1, 1, -1, 1, -1, 1]
        y_delta = [-1, 1, 0, 0, -1, 1, 1, -1]
        for x in range(0, len(x_delta)):
            if seg_binary_inverse[x_coordinate + x_delta[x]][y_coordinate + y_delta[x]] == 0:
                return True
    return False


def create_outline(bmode_slice_data, seg_binary_inv, outline_flag):
    bmode_filtered = seg_binary_inv * bmode_slice_data
    if outline_flag == 1:
        for x in range(0, seg_binary_inv.shape[0] - 1):
            for y in range(0, seg_binary_inv.shape[1] - 1):
                if check_neighbors(x, y, seg_binary_inv):
                    x_delta = [0, 0, 0, -1, 1, -1, 1, -1, 1]
                    y_delta = [0, -1, 1, 0, 0, -1, 1, 1, -1]
                    for z in range(0, len(x_delta)):
                        bmode_filtered[x + x_delta[z]][y + y_delta[z]] = 255
    return bmode_filtered


def create_mask_layer(mask_data, mask_total, lesion_slice_index, seg_binary):
    import numpy as np
    mask_data = mask_data[:, :, lesion_slice_index].transpose()
    mask_voxel_size = {'axial': mask_total.get_qform()[0, 0], 'ele': mask_total.get_qform()[1, 1]}
    mask_ele = [y * mask_voxel_size['ele'] for y in range(0, mask_data.shape[1])]
    mask_ele -= max(mask_ele) / 2
    mask_filtered = mask_data.copy().astype(float) * seg_binary
    mask_filtered[mask_filtered == 0] = np.nan
    mask_filtered = np.squeeze(mask_filtered)
    return mask_filtered


def create_seg_layer(seg_total, bmode_slice_data, lesion_slice_index):
    import numpy as np

    seg_data = seg_total[0]
    seg_meta = seg_total[1]

    # Read relative offset and dimensions of segmentation
    seg_offset_string = seg_meta['Segmentation_ReferenceImageExtentOffset']
    seg_voxel_scale = seg_meta['space directions']
    seg_offset = [int(i) for i in seg_offset_string.split()]

    # Get matrix of segment data for a given slice
    if lesion_slice_index - seg_offset[2] > seg_data.shape[2]:
        raise ValueError("lesion_slice_index outside of prostate capsule")
    seg_data = seg_data[:, :, lesion_slice_index - seg_offset[2]]
    seg_data = seg_data.transpose()

    # Split scaling of segmentation voxels for each dimension
    seg_voxel_size = {'lat': sum(seg_voxel_scale[0]), 'axial': abs(sum(seg_voxel_scale[1])),
                      'ele': abs(sum(seg_voxel_scale[2]))}
    seg_ele = [y * seg_voxel_size['ele'] for y in range(0, seg_data.shape[1])]
    seg_ele -= max(seg_ele) / 2

    xlim = int(bmode_slice_data.shape[0])
    ylim = int(bmode_slice_data.shape[1])

    seg_binary = np.zeros((xlim, ylim))
    for x in range(0, seg_data.shape[0] - 1):
        for y in range(0, seg_data.shape[1] - 1):
                seg_binary[x + seg_offset[1]][y + seg_offset[0]] = 1 * seg_data[x][y]

    return seg_binary
