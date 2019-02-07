def plot_combine(seg_file, bmode_file, capsule_file, lesion_slice_index, bmode_window, bmode_min_level, capsule_window,
                 capsule_min_level, swei_flag, outline_flag, ax, fig):
    import matplotlib.pyplot as plt
    import nibabel as nib
    import nrrd
    import numpy as np

    # Import full segmentation file
    seg_total = nrrd.read(seg_file)
    
    # Split into nrrd files' metadata and image data
    seg_data = seg_total[0]
    seg_meta = seg_total[1]
    
    # Read relative offset and dimensions of segmentation
    seg_offset_string = seg_meta['Segmentation_ReferenceImageExtentOffset']
    seg_voxel_scale = seg_meta['space directions']
    
    # Transform offset dimensions from single string into array of integers
    offset_string = ""
    for digit in seg_offset_string:
        offset_string += str(digit)
    offset_strings = offset_string.split(" ");
    offset_count = 0;
    seg_offset = [0, 0, 0]
    for offset in offset_strings:
        seg_offset[offset_count] = int(offset)
        offset_count += 1
    
    # Get matrix of segment data for a given slice
    if lesion_slice_index - seg_offset[2] > seg_data.shape[2]:
        raise ValueError("lesion_slice_index outside of prostate capsule")
    seg_data = seg_data[:, :, lesion_slice_index - seg_offset[2]]
    seg_data = seg_data.transpose()
         
    # Split scaling of segmentation voxels for each dimension
    seg_voxel_size = {'lat': sum(seg_voxel_scale[0]), 'axial': abs(sum(seg_voxel_scale[1])),
                      'ele': abs(sum(seg_voxel_scale[2]))}
    seg_ele = [y*seg_voxel_size['ele'] for y in range(0, seg_data.shape[1])]
    seg_ele -= max(seg_ele) / 2
     
    # Load B-mode file and split metadata from data 
    bmode_total = nib.load(bmode_file)
    bmode_data = bmode_total.get_data()

    # Read relative scalings of each dimension
    bmode_voxel_size = {'lat': bmode_total.get_qform()[2, 2]}
    bmode_lat = [z*bmode_voxel_size['lat'] for z in range(0, bmode_data.shape[2])]
    bmode_lat -= max(bmode_lat) / 2

    # Get matrix of B-mode data for a given slice
    bmode_data = bmode_data[:, :, lesion_slice_index, 0]
    bmode_data = bmode_data.transpose()
    
    # Split scaling of B-mode voxels for each dimension
    bmode_voxel_size['axial'] = bmode_total.get_qform()[0, 0]
    bmode_voxel_size['ele'] = bmode_total.get_qform()[1, 1]
    bmode_axial = [x*bmode_voxel_size['axial'] for x in range(0, bmode_data.shape[0])]
    bmode_ele = [y*bmode_voxel_size['ele'] for y in range(0, bmode_data.shape[1])]
    bmode_ele -= max(bmode_ele) / 2
    
    # Load ARFI file and split metadata from data
    capsule_total = nib.load(capsule_file)
    capsule_data = capsule_total.dataobj[..., :]

    # Read relative scalings of each dimension
    capsule_data = capsule_data[:, :, lesion_slice_index]
    capsule_data = capsule_data.transpose()
    capsule_voxel_size = {'axial': capsule_total.get_qform()[0, 0], 'ele': capsule_total.get_qform()[1, 1]}
    capsule_ele = [y*capsule_voxel_size['ele'] for y in range(0, capsule_data.shape[1])]
    capsule_ele -= max(capsule_ele) / 2
    
    # Get final resolution of the image
    xlim = int(bmode_data.shape[0])
    ylim = int(bmode_data.shape[1])
    
    # Create binary matrix of which points are segmented
    seg_binary = np.zeros((xlim, ylim))    
    for x in range(0, seg_data.shape[0] - 1):
        for y in range(0, seg_data.shape[1] - 1):
                seg_binary[x + seg_offset[1]][y + seg_offset[0]] = 1 * seg_data[x][y]

    # Create inverse of the binary matrix
    seg_binary_inv = 1 - seg_binary
    
    # Create array of ARFI values where segmentation is
    capsule_filtered = seg_binary * capsule_data
    capsule_filtered[capsule_filtered == 0] = np.NaN

    # Create B-mode array where segmentation is not
    bmode_filtered = seg_binary_inv * bmode_data
    if(outline_flag == 1):
        for x in range(0, seg_binary_inv.shape[0] - 1):
            for y in range(0, seg_binary_inv.shape[1] - 1):
                if checkNeighbors(x, y, seg_binary_inv):
                    x_delta = [0, 0, 0, -1, 1, -1, 1, -1, 1]
                    y_delta = [0, -1, 1, 0, 0, -1, 1, 1, -1]
                    for z in range(0, len(x_delta)):
                        bmode_filtered[x+x_delta[z]][y+y_delta[z]] = 255




    # Show the arrays on the same set of axes w/ different colormaps
    ax.imshow(bmode_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)], cmap='gray',
              vmin=bmode_min_level, vmax=bmode_min_level + bmode_window)
    if swei_flag == 0:
        ax.imshow(capsule_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)],
                            cmap='copper', vmin=capsule_min_level, vmax=capsule_min_level + capsule_window)
        plt.title("ARFI Capsule/B-mode Background")
    else:
        cax = ax.imshow(capsule_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)],
                        cmap='inferno_r', vmin=capsule_min_level, vmax=capsule_min_level + capsule_window)
        plt.title("SWEI Capsule/B-mode Background")
        fig.colorbar(cax)
    
    # Add title, labels, and colorbar
    ax.set_xlabel("Elevation (mm)")
    ax.set_ylabel("Depth (mm)")


def checkNeighbors(x_coordinate, y_coordinate, seg_binary_inverse):
    if seg_binary_inverse[x_coordinate][y_coordinate] != 0:
        x_delta = [0, 0, -1, 1, -1, 1, -1, 1]
        y_delta = [-1, 1, 0, 0, -1, 1, 1, -1]
        for x in range(0, len(x_delta)):
            if seg_binary_inverse[x_coordinate + x_delta[x]][y_coordinate + y_delta[x]] == 0:
                return True
    return False
