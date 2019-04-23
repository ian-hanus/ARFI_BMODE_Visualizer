'''
Created on Nov 26, 2018

@author: Ian_Hanus 
'''
import matplotlib.pylab as plt
import os
from src.SegOutline import plot_combine
import pylab
import gc
from src.CoronalPlot import plot_coronal_test

# Folder path containing seg, arfi, and bmode files
f = open(os.path.join(os.environ["HOMEPATH"], "InfoHolder.txt"))
stringInputs = f.read()
inputs = stringInputs.split(", ")
f.close()

# Call function to plot ARFI segment with B-mode background
# for x in range(24, 240):
#     print(x)
fig, ax = plt.subplots()
plot_combine(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], int(inputs[5]), float(inputs[6]), float(inputs[7]),
             float(inputs[8]), float(inputs[9]), int(inputs[10]), int(inputs[11]), inputs[12], int(inputs[13]), ax, fig)
    # pylab.close('all')
plt.show()