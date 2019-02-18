import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

# SegDisplay

class SegDisplay(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Segmentation Display"
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
    parameters_collapsible_button = ctk.ctkCollapsibleButton()
    parameters_collapsible_button.text = "Parameters"
    self.layout.addWidget(parameters_collapsible_button)
    parameters_form_layout = qt.QFormLayout(parameters_collapsible_button)

    # B-mode volume selector
    self.bmode_selector = slicer.qMRMLNodeComboBox()
    self.bmode_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.bmode_selector.selectNodeUponCreation = True
    self.bmode_selector.addEnabled = False
    self.bmode_selector.removeEnabled = False
    self.bmode_selector.noneEnabled = False
    self.bmode_selector.showHidden = False
    self.bmode_selector.showChildNodeTypes = False
    self.bmode_selector.setMRMLScene( slicer.mrmlScene )
    self.bmode_selector.setToolTip( "Pick the B-mode volume." )
    parameters_form_layout.addRow("B-mode Volume: ", self.bmode_selector)
    
    # ARFI volume selector
    self.arfi_selector = slicer.qMRMLNodeComboBox()
    self.arfi_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.arfi_selector.selectNodeUponCreation = True
    self.arfi_selector.addEnabled = False
    self.arfi_selector.removeEnabled = False
    self.arfi_selector.noneEnabled = False
    self.arfi_selector.showHidden = False
    self.arfi_selector.showChildNodeTypes = False
    self.arfi_selector.setMRMLScene( slicer.mrmlScene )
    self.arfi_selector.setToolTip( "Pick the ARFI volume." )
    parameters_form_layout.addRow("ARFI Volume: ", self.arfi_selector)

    # SWEI volume selector
    self.swei_selector = slicer.qMRMLNodeComboBox()
    self.swei_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.swei_selector.selectNodeUponCreation = True
    self.swei_selector.addEnabled = False
    self.swei_selector.removeEnabled = False
    self.swei_selector.noneEnabled = False
    self.swei_selector.showHidden = False
    self.swei_selector.showChildNodeTypes = False
    self.swei_selector.setMRMLScene( slicer.mrmlScene )
    self.swei_selector.setToolTip( "Pick the SWEI volume." )
    parameters_form_layout.addRow("SWEI Volume: ", self.swei_selector)
    
    # Segmentation selector
    self.segmentation_selector = slicer.qMRMLNodeComboBox()
    self.segmentation_selector.nodeTypes = ["vtkMRMLSegmentationNode"]
    self.segmentation_selector.selectNodeUponCreation = True
    self.segmentation_selector.addEnabled = False
    self.segmentation_selector.removeEnabled = False
    self.segmentation_selector.noneEnabled = False
    self.segmentation_selector.showHidden = False
    self.segmentation_selector.showChildNodeTypes = False
    self.segmentation_selector.setMRMLScene( slicer.mrmlScene )
    self.segmentation_selector.setToolTip( "Pick the capsule segmentation." )
    parameters_form_layout.addRow("Segmentation: ", self.segmentation_selector)

    # Arfi Mask Selector
    self.mask_selector = slicer.qMRMLNodeComboBox()
    self.mask_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.mask_selector.selectNodeUponCreation = True
    self.mask_selector.addEnabled = False
    self.mask_selector.removeEnabled = False
    self.mask_selector.noneEnabled = False
    self.mask_selector.showHidden = False
    self.mask_selector.showChildNodeTypes = False
    self.mask_selector.setMRMLScene( slicer.mrmlScene )
    self.mask_selector.setToolTip( "Pick the Mask volume." )
    parameters_form_layout.addRow("Mask Volume: ", self.mask_selector)


    #
    # Apply button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = True
    parameters_form_layout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.bmode_selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.arfi_selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.swei_selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.segmentation_selector.connect("currentNodeChanged(vtkMRMLSegmentationNode*)", self.onSelect)
    self.mask_selector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Radio buttons
    self.arfiButton = qt.QRadioButton("ARFI Capsule")
    self.arfiButton.setChecked(True)
    self.sweiButton = qt.QRadioButton("SWEI Capsule")
    parameters_form_layout.addRow("Capsule Type:", self.arfiButton)
    parameters_form_layout.addRow("", self.sweiButton)

    # Outline checkbox
    self.outlineCheck = qt.QCheckBox("")
    self.outlineCheck.setChecked(False)
    parameters_form_layout.addRow("White Outline Around Capsule: ", self.outlineCheck)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def onSelect(self):
    self.applyButton.enabled = self.bmode_selector.currentNode() and self.arfi_selector.currentNode() and self.segmentation_selector.currentNode() and self.swei_selector.currentNode() and self.mask_selector.currentNode()

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
    bmodeNode = self.bmode_selector.currentNode()
    arfiNode = self.arfi_selector.currentNode()
    sweiNode = self.swei_selector.currentNode()
    segNode = self.segmentation_selector.currentNode()
    maskNode = self.mask_selector.currentNode()

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

    outline = 0
    if self.outlineCheck.isChecked():
      outline = 1

    test_file = open(os.path.join(os.environ["HOMEPATH"], "InfoHolder.txt"), 'w')
    
    test_file.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (segFile, bmodeFile, capsuleFile, maskFile, sliceIndex, bmodeWindow,
                                                    bmodeLevelMin, capsuleWindow, capsuleLevelMin, sweiFlag, outline))

    
    test_file.close()


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


