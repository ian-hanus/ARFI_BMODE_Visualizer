import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

# SegDisplay

class SegDisplay(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Segmentation Display" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = [""]
    self.parent.helpText += self.getDefaultModuleDocumentationLink()


#
# SegDisplayWidget
#

class SegDisplayWidget(ScriptedLoadableModuleWidget):
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Parameters Area
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # B-mode volume selector
    self.bmodeSelector = slicer.qMRMLNodeComboBox()
    self.bmodeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.bmodeSelector.selectNodeUponCreation = True
    self.bmodeSelector.addEnabled = False
    self.bmodeSelector.removeEnabled = False
    self.bmodeSelector.noneEnabled = False
    self.bmodeSelector.showHidden = False
    self.bmodeSelector.showChildNodeTypes = False
    self.bmodeSelector.setMRMLScene( slicer.mrmlScene )
    self.bmodeSelector.setToolTip( "Pick the B-mode volume." )
    parametersFormLayout.addRow("B-mode Volume: ", self.bmodeSelector)
    
    # ARFI volume selector
    self.arfiSelector = slicer.qMRMLNodeComboBox()
    self.arfiSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.arfiSelector.selectNodeUponCreation = True
    self.arfiSelector.addEnabled = False
    self.arfiSelector.removeEnabled = False
    self.arfiSelector.noneEnabled = False
    self.arfiSelector.showHidden = False
    self.arfiSelector.showChildNodeTypes = False
    self.arfiSelector.setMRMLScene( slicer.mrmlScene )
    self.arfiSelector.setToolTip( "Pick the ARFI volume." )
    parametersFormLayout.addRow("ARFI Volume: ", self.arfiSelector)

    # SWEI volume selector
    self.sweiSelector = slicer.qMRMLNodeComboBox()
    self.sweiSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.sweiSelector.selectNodeUponCreation = True
    self.sweiSelector.addEnabled = False
    self.sweiSelector.removeEnabled = False
    self.sweiSelector.noneEnabled = False
    self.sweiSelector.showHidden = False
    self.sweiSelector.showChildNodeTypes = False
    self.sweiSelector.setMRMLScene( slicer.mrmlScene )
    self.sweiSelector.setToolTip( "Pick the SWEI volume." )
    parametersFormLayout.addRow("SWEI Volume: ", self.sweiSelector)
    
    # Segmentation selector
    self.segmentationSelector = slicer.qMRMLNodeComboBox()
    self.segmentationSelector.nodeTypes = ["vtkMRMLSegmentationNode"]
    self.segmentationSelector.selectNodeUponCreation = True
    self.segmentationSelector.addEnabled = False
    self.segmentationSelector.removeEnabled = False
    self.segmentationSelector.noneEnabled = False
    self.segmentationSelector.showHidden = False
    self.segmentationSelector.showChildNodeTypes = False
    self.segmentationSelector.setMRMLScene( slicer.mrmlScene )
    self.segmentationSelector.setToolTip( "Pick the capsule segmentation." )
    parametersFormLayout.addRow("Segmentation: ", self.segmentationSelector)

    # Arfi Mask Selector
    self.maskSelector = slicer.qMRMLNodeComboBox()
    self.maskSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.maskSelector.selectNodeUponCreation = True
    self.maskSelector.addEnabled = False
    self.maskSelector.removeEnabled = False
    self.maskSelector.noneEnabled = False
    self.maskSelector.showHidden = False
    self.maskSelector.showChildNodeTypes = False
    self.maskSelector.setMRMLScene( slicer.mrmlScene )
    self.maskSelector.setToolTip( "Pick the Mask volume." )
    parametersFormLayout.addRow("Mask Volume: ", self.maskSelector)


    #
    # Apply button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = True
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.bmodeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.arfiSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.sweiSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.segmentationSelector.connect("currentNodeChanged(vtkMRMLSegmentationNode*)", self.onSelect)
    self.maskSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Radio buttons
    self.arfiButton = qt.QRadioButton("ARFI Capsule")
    self.arfiButton.setChecked(True)
    self.sweiButton = qt.QRadioButton("SWEI Capsule")
    parametersFormLayout.addRow("Capsule Type:", self.arfiButton)
    parametersFormLayout.addRow("", self.sweiButton)

    # Outline checkbox
    self.outlineCheck = qt.QCheckBox("")
    self.outlineCheck.setChecked(False)
    parametersFormLayout.addRow("White Outline Around Capsule: ", self.outlineCheck)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()



  def onSelect(self):
    self.applyButton.enabled = self.bmodeSelector.currentNode() and self.arfiSelector.currentNode() and self.segmentationSelector.currentNode() and self.sweiSelector.currentNode() and self.maskSelector.currentNode()



  def onApplyButton(self):  
    lm = slicer.app.layoutManager()
    red = lm.sliceWidget('Red')
    redLogic = red.sliceLogic()
    # Print current slice offset position
    redOffset = redLogic.GetSliceOffset()
    sliceIndex = redLogic.GetSliceIndexFromOffset(redOffset)

    sweiImage = self.sweiButton.isChecked()

    def pathFromNode(node):
        storageNode=node.GetStorageNode()
        if storageNode is not None: # loaded via drag-drop
            filepath=storageNode.GetFullNameFromFileName()
        else:
            instanceUIDs=node.GetAttribute('DICOM.instanceUIDs').split()
            filepath=slicer.dicomDatabase.fileForInstance(instUids[0])
        return filepath
    
    # Get file names to plug into runDisplay
    bmodeNode = self.bmodeSelector.currentNode()
    arfiNode = self.arfiSelector.currentNode()
    sweiNode = self.sweiSelector.currentNode()
    segNode = self.segmentationSelector.currentNode()
    maskNode = self.maskSelector.currentNode()

    bmodeVolumeDisplay = bmodeNode.GetScalarVolumeDisplayNode()
    bmodeWindow = bmodeVolumeDisplay.GetWindow()
    bmodeLevelMin = bmodeVolumeDisplay.GetWindowLevelMin()

    bmodeFile = pathFromNode(bmodeNode)
    if sweiImage:
      capsuleNode = sweiNode
      sweiFlag = 1
    else:
      capsuleNode = arfiNode
      sweiFlag = 0

    capsuleVolumeDisplay = capsuleNode.GetScalarVolumeDisplayNode()
    capsuleWindow = capsuleVolumeDisplay.GetWindow()
    capsuleLevelMin = capsuleVolumeDisplay.GetWindowLevelMin()

    capsuleFile = pathFromNode(capsuleNode)
    segFile = pathFromNode(segNode)
    maskFile = pathFromNode(maskNode)

    outline = 0;
    if self.outlineCheck.isChecked():
      outline = 1

    f = open("C:\Users\Ian_Hanus\Desktop\SlicerCustomVisualization\CustomVisualization\DisplayPlot\myInput.txt", "w+")
    
    f.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (segFile, bmodeFile, capsuleFile, maskFile, sliceIndex, bmodeWindow,
                                                    bmodeLevelMin, capsuleWindow, capsuleLevelMin, sweiFlag, outline))

    
    f.close()


class SegDisplayLogic(ScriptedLoadableModuleLogic):

  def hasImageData(self,volumeNode):

    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qimage = ctk.ctkWidgetsUtils.grabWidget(widget)
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('SegDisplayTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class SegDisplayTest(ScriptedLoadableModuleTest):

  def setUp(self):
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    self.setUp()
    self.test_SegDisplay1()

  def test_SegDisplay1(self):
    self.delayDisplay("Starting the test")
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = SegDisplayLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
