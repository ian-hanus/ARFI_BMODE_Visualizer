'''
Created on Nov 26, 2018

@author: Ian_Hanus 
'''
import matplotlib.pyplot as plt
from src.SegOutline import plot_combine

# Folder path containing seg, arfi, and bmode files
inputFile = "C:/Users/Ian_Hanus/Desktop/SlicerCustomVisualization/CustomVisualization/DisplayPlot/myInput.txt"
f = open(inputFile)
stringInputs = f.read()

inputs = stringInputs.split(", ")

# Call function to plot ARFI segment with B-mode background
fig, ax = plt.subplots()
plot_combine(inputs[0], inputs[1], inputs[2], int(inputs[3]), ax, fig)
plt.show()
