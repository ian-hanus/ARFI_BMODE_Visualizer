# Using the Segmentation Display Tool
### Instructions in Slicer
1. Place the zipped "ArfiBmodeSegDisplay.zip" file in the desired location
2. Unzip the file
3. Open slicer, and open the "Extension Wizard" module from the modules dropdown
4. Click "Select Extension" and select the "ArfiBmodeSegDisplay" folder
5. When prompted, check "Add selected module to search paths" and click ok
6. Extension should now be available in modules dropdown as "Segmentation Display"
7. Select all of the proper volumes and preferences in the module and click apply


### Instructions in Python
1. Open the runDisplay.py file
2. Run the file
3. A single matplotlib image should pop up containing the frame that you had specified in slicer

### Changing the program
1. Adding nodes in the slicer extension can be done by editing the SegDisplay.py file (make sure to read the documentation
for the Slicer API before attempting to add new features)
2. The functionality of the program occurs in the SegOutline.py file. Notably this includes commenting out the code
specifying a lesion outline if one is not chosen, as I did not have time to add a toggle switch in the Slicer GUI yet.
All of the preference based plotting such as colormaps can be edited by changing the preferences in the ax.imshow lines.

