# encoding: utf-8

####################################################################################################
#
# Filter with dialog Plugin
#
# Read the docs:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
# For help on the use of Interface Builder:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
####################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *

class Shadow(FilterWithDialog):
	
	# Definitions of IBOutlets
	dialog = objc.IBOutlet()
	offsetField = objc.IBOutlet()
	distanceXField = objc.IBOutlet()
	distanceYField = objc.IBOutlet()
	
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Shadow',
			'de': u'Schatten',
			'fr': u'Ombre',
			'nl': u'Schaduw',
			'es': u'Sombrear'
		})

		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)
	
	# On dialog show
	def start(self):
		# Set defaults
		Glyphs.registerDefault('com.mekkablue.Shadow.offset', 15.0)
		Glyphs.registerDefault('com.mekkablue.Shadow.distanceX', 15.0)
		Glyphs.registerDefault('com.mekkablue.Shadow.distanceY', 15.0)

		# Set value of text field
		self.offsetField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.offset'])
		self.distanceXField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.distanceX'])
		self.distanceYField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.distanceY'])
		
		# Set focus to text field
		self.offsetField.becomeFirstResponder()
		
		# Trigger redraw
		self.update()
		
	# Setting Offset, triggered by UI
	@objc.IBAction
	def setOffset_( self, sender ):
		# Store value coming in from dialog
		Glyphs.defaults['com.mekkablue.Shadow.offset'] = sender.floatValue()
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
	
	# Actual filter
	def filter(self, layer, inEditView, customParameters):
		# fallback values:
		offset, distanceX, distanceY = 15, 15, 15
		
		# Called on font export, get value from customParameters
		if customParameters.has_key('offset'):
			offset = customParameters['offset']
		if customParameters.has_key('distanceX'):
			distanceX = customParameters['distanceX']
		if customParameters.has_key('distanceY'):
			distanceY = customParameters['distanceY']

		# Called through UI, use stored value
		if inEditView:
			offset = float(Glyphs.defaults['com.mekkablue.Shadow.offset'])
			distanceX = float(Glyphs.defaults['com.mekkablue.Shadow.distanceX'])
			distanceY = float(Glyphs.defaults['com.mekkablue.Shadow.distanceY'])

		offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
		roundFilter = NSClassFromString("GlyphsFilterRoundCorner")
		
		layer.decomposeComponents()
		offsetLayer = layer.copy()
		
		offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_(
						offsetLayer, offset, offset,
						False, False, 0.5, None,None)

		roundFilter.roundLayer_radius_checkSelection_visualCorrect_grid_(
						offsetLayer, offset,
						False, True, False )
		
		# Create and offset Shadow only if it has a distance:
		if distanceX != 0.0 or distanceY != 0.0:
			shadowLayer = offsetLayer.copy()
			shadowLayer.applyTransform( (1,0,0,1,distanceX,-distanceY) )
			try:
				offsetLayer.appendLayer_(shadowLayer)
			except:
				self.mergeLayerIntoLayer(shadowLayer,offsetLayer)
		
		offsetLayer.removeOverlap()
		layer.removeOverlap()
		try:
			layer.appendLayer_(offsetLayer)
		except:
			self.mergeLayerIntoLayer(offsetLayer,layer)
		layer.correctPathDirection()

	def mergeLayerIntoLayer(self, sourceLayer, targetLayer):
		for p in sourceLayer.paths:
			targetLayer.addPath_(p.copy())
	
	def generateCustomParameter( self ):
		return "%s; offset:%s; distanceX:%s; distanceY:%s" % (
			self.__class__.__name__,
			Glyphs.defaults['com.mekkablue.Shadow.offset'],
			Glyphs.defaults['com.mekkablue.Shadow.distanceX'],
			Glyphs.defaults['com.mekkablue.Shadow.distanceY'],
			)
		
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
