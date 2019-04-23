# Using the Segmentation Display Tool
### Instructions in Slicer
1. Under the modules dropdown, select Extension Wizard
2. Click "Select Extension" and navigate to the downloaded ArfiBmodeSegDisplay folder
3. Go back to the modules dropdown and select the newly added "Segmentation Display" module
4. Select all of the proper volumes next to the labels and hit apply
5. Open the runDisplay.py file in the Python IDE of your choice (currently using Pycharm but should work with any)


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

