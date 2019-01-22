def plot_combine(seg_file, bmode_file, arfi_file, lesion_slice_index, ax, fig):
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
    seg_voxel_size = {'lat': sum(seg_voxel_scale[0])}
    seg_voxel_size['axial'] = abs(sum(seg_voxel_scale[1]))
    seg_voxel_size['ele'] = abs(sum(seg_voxel_scale[2]))
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
    arfi_total = nib.load(arfi_file)
    arfi_data = arfi_total.get_data()
    
    # Read relative scalings of each dimension
    arfi_data = arfi_data[:, :, lesion_slice_index, 0]
    arfi_data = arfi_data.transpose()
    arfi_voxel_size = {'axial': arfi_total.get_qform()[0, 0], 'ele': arfi_total.get_qform()[1, 1]}
    arfi_ele = [y*arfi_voxel_size['ele'] for y in range(0, arfi_data.shape[1])]
    arfi_ele -= max(arfi_ele) / 2
    
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
    arfi_filtered = seg_binary * arfi_data
    arfi_filtered[arfi_filtered == 0] = np.NaN        
    
    # Create B-mode array where segmentation is not
    bmode_filtered = seg_binary_inv * bmode_data
    
    # Show the arrays on the same set of axes w/ different colormaps
    ax.imshow(bmode_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)], cmap='gray')
    cax = ax.imshow(arfi_filtered, extent=[min(bmode_ele), max(bmode_ele), min(bmode_axial), max(bmode_axial)],
                    cmap='copper')
    
    # Add title, labels, and colorbar
    ax.set_xlabel("Elevation (mm)")
    ax.set_ylabel("Depth (mm)")
    plt.title("ARFI Capsule/B-mode Background")
    fig.colorbar(cax)
