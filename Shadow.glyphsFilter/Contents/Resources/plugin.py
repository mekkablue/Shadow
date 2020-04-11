# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#	Filter with dialog Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
#	For help on the use of Interface Builder:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

import objc, math
from GlyphsApp import *
from GlyphsApp.plugins import *

from AppKit import NSAffineTransform, NSAffineTransformStruct
from Foundation import NSClassFromString

@objc.python_method
def offsetTheLayer( thisLayer, offsetX, offsetY, makeStroke=False, position=0.5, autoStroke=False ):
	offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
	try:
		# GLYPHS 3:	
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
			thisLayer,
			offsetX, offsetY, # horizontal and vertical offset
			makeStroke,     # if True, creates a stroke
			autoStroke,     # if True, distorts resulting shape to vertical metrics
			position,       # stroke distribution to the left and right, 0.5 = middle
			None, None, None, 0, 0, False )
	except:
		# GLYPHS 2:
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_(
			thisLayer,
			offsetX, offsetY, # horizontal and vertical offset
			makeStroke,     # if True, creates a stroke
			autoStroke,     # if True, distorts resulting shape to vertical metrics
			position,       # stroke distribution to the left and right, 0.5 = middle
			None, None )


@objc.python_method
def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct() # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX,shiftY)
	if skew:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(skew))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		myTransform.appendTransform_(skewTransform)
	return myTransform

class Shadow(FilterWithDialog):
	
	# Definitions of IBOutlets
	dialog = objc.IBOutlet()
	offsetField = objc.IBOutlet()
	distanceXField = objc.IBOutlet()
	distanceYField = objc.IBOutlet()
	shouldRoundCheckbox = objc.IBOutlet()
	keepSidebearingsCheckbox = objc.IBOutlet()
	
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Shadow',
			'de': u'Schatten',
			'fr': u'Ombreur',
			'nl': u'Schaduw',
			'es': u'Sombrear',
			'zh': u'🌖阴影',
		})
		
		self.actionButtonLabel = Glyphs.localize({
			'en': u'Apply',
			'de': u'Anwenden',
			'fr': u'Ombrer',
			'nl': u'Toepassen',
			'es': u'Sombrear',
			'zh': u'确定',
		})

		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)
	
	# On dialog show
	@objc.python_method
	def start(self):
		# Set defaults
		Glyphs.registerDefault('com.mekkablue.Shadow.offset', 15.0)
		Glyphs.registerDefault('com.mekkablue.Shadow.offsetY', 15.0)
		Glyphs.registerDefault('com.mekkablue.Shadow.distanceX', 15.0)
		Glyphs.registerDefault('com.mekkablue.Shadow.distanceY', 15.0)
		Glyphs.registerDefault('com.mekkablue.Shadow.shouldRound', 1)
		Glyphs.registerDefault('com.mekkablue.Shadow.keepSidebearings', 1)

		# Set value of text field
		self.offsetField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.offset'])
		self.offsetField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.offsetY'])
		self.distanceXField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.distanceX'])
		self.distanceYField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.distanceY'])
		self.shouldRoundCheckbox.setState_(Glyphs.defaults['com.mekkablue.Shadow.shouldRound'])
		self.keepSidebearingsCheckbox.setState_(Glyphs.defaults['com.mekkablue.Shadow.keepSidebearings'])
		
		# Set focus to text field
		self.offsetField.becomeFirstResponder()
		
		# Trigger redraw
		self.update()
		
	# Setting Offset, triggered by UI
	@objc.IBAction
	def setOffset_( self, sender ):
		# Store value coming in from dialog
		if ";" in sender.stringValue():
			try:
				Glyphs.defaults['com.mekkablue.Shadow.offset'] = int(sender.stringValue().split(";")[0].strip())
				Glyphs.defaults['com.mekkablue.Shadow.offsetY'] = int(sender.stringValue().split(";")[1].strip())
			except:
				# exit gracefully (probably user did not finish entering his values)
				pass
		else:
			Glyphs.defaults['com.mekkablue.Shadow.offset'] = sender.intValue()
			Glyphs.defaults['com.mekkablue.Shadow.offsetY'] = sender.intValue()
		# Trigger redraw
		self.update()

	@objc.IBAction
	def setDistanceX_( self, sender ):
		Glyphs.defaults['com.mekkablue.Shadow.distanceX'] = sender.floatValue()
		self.update()

	@objc.IBAction
	def setDistanceY_( self, sender ):
		Glyphs.defaults['com.mekkablue.Shadow.distanceY'] = sender.floatValue()
		self.update()

	@objc.IBAction
	def setShouldRound_( self, sender ):
		Glyphs.defaults['com.mekkablue.Shadow.shouldRound'] = sender.state()
		self.update()

	@objc.IBAction
	def setKeepSidebearings_( self, sender ):
		Glyphs.defaults['com.mekkablue.Shadow.keepSidebearings'] = sender.state()
		self.update()
	
	# Actual filter
	@objc.python_method
	def filter(self, thisLayer, inEditView, customParameters):
		if not thisLayer is None: # circumvents a bug in 2.5b
			# fallback values:
			offset, offsetY, distanceX, distanceY = 15, 15, 15, 15
			shouldRound, keepSidebearings = 1, 0
			
			if len(customParameters) > 0:
				# Called on font export, get value from customParameters
				if 'offset' in customParameters:
					offset = customParameters['offset']
				if 'offsetY' in customParameters:
					offsetY = customParameters['offsetY']
				if 'distanceX' in customParameters:
					distanceX = customParameters['distanceX']
				if 'distanceY' in customParameters:
					distanceY = customParameters['distanceY']
				if 'shouldRound' in customParameters:
					distanceY = customParameters['shouldRound']
				if 'keepSidebearings' in customParameters:
					distanceY = customParameters['keepSidebearings']

			# Called through UI, use stored value
			else:
				offset = int(Glyphs.defaults['com.mekkablue.Shadow.offset'])
				offsetY = int(Glyphs.defaults['com.mekkablue.Shadow.offsetY'])
				distanceX = float(Glyphs.defaults['com.mekkablue.Shadow.distanceX'])
				distanceY = float(Glyphs.defaults['com.mekkablue.Shadow.distanceY'])
				shouldRound = bool(Glyphs.defaults['com.mekkablue.Shadow.shouldRound'])
				keepSidebearings = bool(Glyphs.defaults['com.mekkablue.Shadow.keepSidebearings'])

			thisLayer.decomposeComponents()
			offsetLayer = thisLayer.copy()
			originalLSB = thisLayer.LSB
			originalRSB = thisLayer.RSB
			originalBBoxWidth = thisLayer.bounds.size.width
			originalWidth = thisLayer.width
		
			# Create offset rim:
			if offset != 0.0:
				offsetTheLayer( offsetLayer, offset, offsetY, makeStroke=False, position=0.5, autoStroke=False )
				
				if shouldRound:
					roundFilter = NSClassFromString("GlyphsFilterRoundCorner")
					roundFilter.roundLayer_radius_checkSelection_visualCorrect_grid_(
									offsetLayer, 
									offset,
									False, True, False )
		
			# Create and offset Shadow only if it has a distance:
			if distanceX != 0.0 or distanceY != 0.0:
				shadowLayer = offsetLayer.copy()
				shadowLayer.applyTransform( (1,0,0,1,distanceX,-distanceY) )
				
				# only create shadow if there is no offset rim:
				if offset == 0.0:
					# prepare thisLayers for subtraction:
					thisLayer.removeOverlap()
					shadowLayer.removeOverlap()
					
					# subtract:
					subtractedPaths = [p for p in shadowLayer.paths]
					pathOperator = NSClassFromString("GSPathOperator").alloc().init()
					pathOperator.subtractPaths_from_error_debug_(
						[p for p in thisLayer.paths],
						subtractedPaths,
						None, False
					)
					
					# transfer the subtraction result into the main thisLayer, and we are done:
					try:
						thisLayer.shapes = subtractedPaths
					except:
						thisLayer.paths = subtractedPaths
					
				# if there is an offset, merge rim and shadow thisLayers:
				else:
					try:
						offsetLayer.appendLayer_(shadowLayer)
					except:
						self.mergeLayerIntoLayer(shadowLayer,offsetLayer)
		
			thisLayer.removeOverlap()
			
			# if there is an offset, merge original paths with merged rim+shadow paths:
			if offset != 0.0:
				offsetLayer.removeOverlap()
				try:
					thisLayer.appendLayer_(offsetLayer)
				except:
					self.mergeLayerIntoLayer(offsetLayer,thisLayer)
			
			thisLayer.cleanUpPaths()
			thisLayer.correctPathDirection()
			
			if keepSidebearings:
				# shift thisLayer contents so LSB matches:
				shiftX = originalLSB-thisLayer.LSB
				shiftMatrix = transform(shiftX=shiftX).transformStruct()
				try:
					# GLYPHS 3:
					for thisShape in thisLayer.shapes:
						thisShape.applyTransform(shiftMatrix)
				except:
					# GLYPHS 2:
					thisLayer.applyTransform(shiftMatrix)
				
				# adjust width so RSB matches:
				thisLayer.width += thisLayer.bounds.size.width-originalBBoxWidth
				# this messes up the shadow layer in Glyphs 3… WTF
				thisLayer.updateMetrics()

	@objc.python_method
	def mergeLayerIntoLayer(self, sourceLayer, targetLayer):
		for p in sourceLayer.paths:
			try:
				targetLayer.shapes.append(p.copy())
			except:
				targetLayer.paths.append(p.copy())
	
	@objc.python_method
	def generateCustomParameter( self ):
		return "%s; offset:%s; offsetY:%s; distanceX:%s; distanceY:%s; shouldRound:%i; keepSidebearings:%i" % (
			self.__class__.__name__,
			Glyphs.defaults['com.mekkablue.Shadow.offset'],
			Glyphs.defaults['com.mekkablue.Shadow.offsetY'],
			Glyphs.defaults['com.mekkablue.Shadow.distanceX'],
			Glyphs.defaults['com.mekkablue.Shadow.distanceY'],
			Glyphs.defaults['com.mekkablue.Shadow.shouldRound'],
			Glyphs.defaults['com.mekkablue.Shadow.keepSidebearings'],
			)
		
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
