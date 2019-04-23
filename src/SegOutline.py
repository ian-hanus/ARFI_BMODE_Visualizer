def plot_combine(seg_file, bmode_file, capsule_file, mask_file, lesion_file, lesion_slice_index, bmode_window, bmode_min_level, capsule_window,
                 capsule_min_level, swei_flag, outline_flag, slice_type, gray_map, ax, fig):
    import matplotlib.pylab as plt
    import nibabel as nib
    import nrrd
    import numpy as np
    import warnings
    lesion_slice_index = lesion_slice_index
    warnings.filterwarnings("ignore")
    seg_total = nrrd.read(seg_file)
    lesion_seg_total = nrrd.read(lesion_file)
    bmode_total = nib.load(bmode_file)
    capsule_total = nib.load(capsule_file)
    mask_total = nib.load(mask_file)

    mask_data = mask_total.dataobj[..., :]
    bmode_data = bmode_total.get_data()
    capsule_data = capsule_total.dataobj[..., :]
    seg_data = seg_total[0]
    seg_meta = seg_total[1]
    lesion_seg_data = lesion_seg_total[0]
    lesion_seg_meta = lesion_seg_total[1]

    seg_offset_string = seg_meta['Segmentation_ReferenceImageExtentOffset']
    seg_voxel_scale = seg_meta['space directions']
    seg_offset = [int(i) for i in seg_offset_string.split()]

    lesion_seg_offset_string = lesion_seg_meta['Segmentation_ReferenceImageExtentOffset']
    lesion_seg_voxel_scale = lesion_seg_meta['space directions']
    lesion_seg_offset = [int(i) for i in lesion_seg_offset_string.split()]
    lesion_flag = True

    if slice_type == "Green":
        seg_offset_personal = seg_offset[1]
        seg_offset_other = [seg_offset[0], seg_offset[2]]
        lesion_seg_offset_personal = lesion_seg_offset[1]
        lesion_seg_offset_other = [lesion_seg_offset[0], lesion_seg_offset[2]]
        bmode_data_slice = np.flipud(bmode_data[:, lesion_slice_index, :, 0].transpose())
        capsule_data_slice = np.flipud(capsule_data[:, lesion_slice_index, :].transpose())
        mask_data_slice = np.flipud(np.squeeze(mask_data[:, lesion_slice_index, :].transpose()))
        try:
            seg_data_slice = np.flipud(seg_data[:, lesion_slice_index - seg_offset_personal, :].transpose())
        except:
            print("No capsule segmentation in frame")
        try:
            lesion_seg_data_slice = np.flipud(lesion_seg_data[:, lesion_slice_index - lesion_seg_offset_personal, :].transpose())
        except:
            print("No lesion segmentation in frame")
            lesion_flag = True
    elif slice_type == "Yellow":
        seg_offset_personal = seg_offset[0]
        seg_offset_other = [seg_offset[2], seg_offset[1]]
        lesion_seg_offset_personal = lesion_seg_offset[0]
        lesion_seg_offset_other = [lesion_seg_offset[2], lesion_seg_offset[1]]
        bmode_data_slice = np.flipud(bmode_data[lesion_slice_index, :, :, 0].transpose())
        capsule_data_slice = np.flipud(capsule_data[lesion_slice_index, :, :].transpose())
        mask_data_slice = np.flipud(np.squeeze(mask_data[lesion_slice_index, :, :].transpose()))
        try:
            seg_data_slice = np.flipud(seg_data[lesion_slice_index - seg_offset_personal, :, :].transpose())
        except:
            print("No capsule segmentation in frame")
        try:
            lesion_seg_data_slice = np.flipud(lesion_seg_data[lesion_slice_index - lesion_seg_offset_personal, :, :].transpose())
        except:
            lesion_flag = False
            print("No lesion segmentation in frame")
    else:
        seg_offset_personal = seg_offset[2]
        seg_offset_other = [seg_offset[0], seg_offset[1]]
        lesion_seg_offset_personal = lesion_seg_offset[2]
        lesion_seg_offset_other = [lesion_seg_offset[0], lesion_seg_offset[1]]
        print(bmode_data.shape)
        # bmode_data_slice = bmode_data[:, :, lesion_slice_index, 0].transpose()
        bmode_data_slice = bmode_data[:, :, lesion_slice_index].transpose()

        # capsule_data_slice = capsule_data[:, :, lesion_slice_index].transpose()
        # capsule_data = np.flip(np.flip(np.flip(capsule_data,0),1),2)
        capsule_data_slice = capsule_data[:, :, lesion_slice_index].transpose()

        mask_data_slice = np.squeeze(mask_data[:, :, lesion_slice_index].transpose())
        try:
            seg_data_slice = seg_data[:, :, lesion_slice_index - seg_offset_personal].transpose()
        except:
            print("No capsule segmentation in frame")
        try:
            lesion_seg_data_slice = lesion_seg_data[:, :, lesion_slice_index - lesion_seg_offset_personal].transpose()
        except:
            lesion_flag = False
            print("No lesion segmentation in frame")


    bmode_voxel_size = {'lat': bmode_total.get_qform()[2, 2]}
    bmode_lat = [z*bmode_voxel_size['lat'] for z in range(0, bmode_data_slice.shape[0])]
    bmode_lat -= max(bmode_lat) / 2

    bmode_voxel_size['depth'] = bmode_total.get_qform()[0, 0]
    bmode_voxel_size['ele'] = bmode_total.get_qform()[1, 1]
    bmode_ele = [y*bmode_voxel_size['ele'] for y in range(0, bmode_data_slice.shape[1])]
    bmode_ele -= max(bmode_ele) / 2

    capsule_voxel_size = {'axial': capsule_total.get_qform()[0, 0], 'ele': capsule_total.get_qform()[1, 1]}
    capsule_ele = [y*capsule_voxel_size['ele'] for y in range(0, capsule_data_slice.shape[1])]
    capsule_ele -= max(capsule_ele) / 2

    seg_voxel_size = {'lat': sum(seg_voxel_scale[0]), 'axial': abs(sum(seg_voxel_scale[1])),
                      'ele': abs(sum(seg_voxel_scale[2]))}
    seg_ele = [y * seg_voxel_size['ele'] for y in range(0, seg_data.shape[1])]
    seg_ele -= max(seg_ele) / 2

    lesion_seg_voxel_size = {'lat': sum(lesion_seg_voxel_scale[0]), 'axial': abs(sum(lesion_seg_voxel_scale[1])),
                      'ele': abs(sum(lesion_seg_voxel_scale[2]))}
    lesion_seg_ele = [y * lesion_seg_voxel_size['ele'] for y in range(0, lesion_seg_data.shape[1])]
    lesion_seg_ele -= max(lesion_seg_ele) / 2

    xlim = int(bmode_data_slice.shape[0])
    ylim = int(bmode_data_slice.shape[1])

    try:
        seg_binary = np.zeros((xlim, ylim))
        for x in range(0, seg_data_slice.shape[0] - 1):
            for y in range(0, seg_data_slice.shape[1] - 1):
                    seg_binary[x + seg_offset_other[1]][y + seg_offset_other[0]] = 1 * seg_data_slice[x][y]
        seg_binary_inv = 1 - seg_binary
        capsule_filtered = seg_binary * capsule_data_slice
        bmode_filtered = create_outline(bmode_data_slice, seg_binary_inv, outline_flag)
        mask_filtered = create_mask_layer(mask_data_slice, mask_total, seg_binary)
    except :
        print("No capsule segmentation in frame")
        capsule_filtered = np.zeros((int(capsule_data_slice.shape[0]), int(capsule_data_slice.shape[1])))
        bmode_filtered = bmode_data_slice
        mask_filtered = np.zeros((int(capsule_data_slice.shape[0]), int(capsule_data_slice.shape[1])))
        mask_filtered[mask_filtered == 0] = np.NaN
    capsule_filtered[capsule_filtered == 0] = np.NaN

    try:
        lesion_seg_binary = np.zeros((xlim, ylim))
        for x in range(0, lesion_seg_data_slice.shape[0] - 1):
            for y in range(0, lesion_seg_data_slice.shape[1] - 1):
                lesion_seg_binary[x+lesion_seg_offset_other[1]][y+lesion_seg_offset_other[0]] = 1 * lesion_seg_data_slice[x][y]

        lesion_seg_binary_inv = 1 - lesion_seg_binary
        lesion_outline = create_outline_only(bmode_data_slice, lesion_seg_binary_inv)
    except:
        print("No lesion segmentation in frame")

    ax.imshow(bmode_filtered, cmap='gray', vmin=bmode_min_level, vmax=bmode_min_level + bmode_window)
    if swei_flag == 0:
        if gray_map == 1:
            capsule_color = 'gray'
        else:
            capsule_color = 'copper'
        ax.imshow(np.squeeze(capsule_filtered), cmap=capsule_color, vmin=capsule_min_level, vmax=capsule_min_level + capsule_window)
        #ax.imshow(mask_filtered, cmap='winter')
        plt.title("ARFI Capsule/B-mode Background")
    else:
        if gray_map == 1:
            capsule_color = 'gray'
        else:
            capsule_color = 'inferno_r'
        cax = ax.imshow(capsule_filtered, cmap=capsule_color, vmin=capsule_min_level, vmax=capsule_min_level + capsule_window)
        plt.title("SWEI Capsule/B-mode Background")
        fig.colorbar(cax)
    if lesion_flag:
        try:
            if lesion_slice_index < 130 and lesion_slice_index > 91:
                ax.imshow(lesion_outline, cmap='winter')
        except:
            print("No lesion segmentation")
    ax.set_xlabel("Elevation (mm)")
    ax.set_ylabel("Depth (mm)")
    # plt.savefig("Bmode" + str(lesion_slice_index + 3000) + ".png")
    # plt.close(fig)
    return


#
# Check to see if pixel is on the edge of capsule segmentation
#
def check_neighbors(x_coordinate, y_coordinate, seg_binary_inverse):
    if seg_binary_inverse[x_coordinate][y_coordinate] != 0:
        x_delta = [0, 0, -1, 1, -1, 1, -1, 1]
        y_delta = [-1, 1, 0, 0, -1, 1, 1, -1]
        for x in range(0, len(x_delta)):
            if seg_binary_inverse[x_coordinate + x_delta[x]][y_coordinate + y_delta[x]] == 0:
                return True
    return False


#
# Create a white outline around the capsule
#
def create_outline(bmode_data_slice, seg_binary_inv, outline_flag):
    bmode_filtered = seg_binary_inv * bmode_data_slice
    if outline_flag == 1:
        for x in range(0, seg_binary_inv.shape[0] - 1):
            for y in range(0, seg_binary_inv.shape[1] - 1):
                if check_neighbors(x, y, seg_binary_inv):
                    x_delta = [0, 0, 0, -1, 1, -1, 1, -1, 1]
                    y_delta = [0, -1, 1, 0, 0, -1, 1, 1, -1]
                    for z in range(0, len(x_delta)):
                        bmode_filtered[x + x_delta[z]][y + y_delta[z]] = 255
    return bmode_filtered


def create_outline_only(bmode_data_slice, seg_binary_inv):
    import numpy as np
    xlim = int(bmode_data_slice.shape[0])
    ylim = int(bmode_data_slice.shape[1])

    outline_only = np.zeros((xlim, ylim))
    for x in range(0, seg_binary_inv.shape[0] - 1):
        for y in range(0, seg_binary_inv.shape[1] - 1):
            if check_neighbors(x, y, seg_binary_inv):
                x_delta = [0, 0, 0, -1, 1, -1, 1, -1, 1]
                y_delta = [0, -1, 1, 0, 0, -1, 1, 1, -1]
                for z in range(0, len(x_delta)):
                    outline_only[x + x_delta[z]][y + y_delta[z]] = 255
            else:
                outline_only[x][y] = np.NaN
    return outline_only


#
# Create a binary map inside the capsule segmentation detailing where the ARFI signal is low confidence and should
# be blocked
#
def create_mask_layer(mask_data_slice, mask_total, seg_binary):
    import numpy as np
    mask_voxel_size = {'depth': mask_total.get_qform()[0, 0], 'ele': mask_total.get_qform()[1, 1]}
    mask_ele = [y * mask_voxel_size['ele'] for y in range(0, mask_data_slice.shape[1])]
    mask_ele -= max(mask_ele) / 2
    mask_filtered = mask_data_slice.copy().astype(float) * seg_binary
    mask_filtered[mask_filtered == 0] = np.NaN
    mask_filtered = mask_filtered * 1.0
    return mask_filtered



# extent=[min(bmode_ele), max(bmode_ele), min(bmode_depth), max(bmode_depth)],
