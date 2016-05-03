# encoding: utf-8

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


from GlyphsApp.plugins import *

class Shadow(FilterWithDialog):

	# Definitions of IBOutlets
	
	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()

	# Text field in dialog
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
		self.loadNib('IBdialog')

	# On dialog show
	def start(self):

		# Set default setting if not present
		defaults = {
			'com.mekkablue.Shadow.offset': 15.0,
			'com.mekkablue.Shadow.distanceX': 15.0,
			'com.mekkablue.Shadow.distanceY': 15.0
		}
		for key in defaults.keys():
			if not Glyphs.defaults[key]:
				Glyphs.defaults[key] = defaults[key]

		# Set value of text field
		self.offsetField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.offset'])
		self.distanceXField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.distanceX'])
		self.distanceYField.setStringValue_(Glyphs.defaults['com.mekkablue.Shadow.distanceY'])
		
		# Set focus to text field
		self.offsetField.becomeFirstResponder()

	# Setting Offset, triggered by UI
	@objc.IBAction
	def setOffset_( self, sender ):
		# Store value coming in from dialog
		Glyphs.defaults['com.mekkablue.Shadow.offset'] = sender.floatValue()
		# Trigger redraw
		self.update()

	# Setting x Distance, triggered by UI
	@objc.IBAction
	def setDistanceX_( self, sender ):
		# Store value coming in from dialog
		Glyphs.defaults['com.mekkablue.Shadow.distanceX'] = sender.floatValue()
		# Trigger redraw
		self.update()

	# Setting y Distance, triggered by UI
	@objc.IBAction
	def setDistanceY_( self, sender ):
		# Store value coming in from dialog
		Glyphs.defaults['com.mekkablue.Shadow.distanceY'] = sender.floatValue()
		# Trigger redraw
		self.update()

	# Actual filter
	def filter(self, layer, inEditView, customParameters):
		
		# Called on font export, get value from customParameters
		if customParameters.has_key('offset'):
			offset = customParameters['offset']
		# Called through UI, use stored value
		else:
			offset = float(Glyphs.defaults['com.mekkablue.Shadow.offset'])

		if customParameters.has_key('distanceX'):
			distanceX = customParameters['distanceX']
		else:
			distanceX = float(Glyphs.defaults['com.mekkablue.Shadow.distanceX'])
			
		if customParameters.has_key('distanceY'):
			distanceY = customParameters['distanceY']
		else:
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
		className = self.__class__.__name__
		parameterString = "%s; " % className
		for key in ("offset", "distanceX", "distanceY"):
			parameterString += "%s:%s; " % ( key, Glyphs.defaults['com.mekkablue.%s.%s'%(className,key)] )
			
		return parameterString.strip()[:-1]
