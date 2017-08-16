def classFactory(iface):
	''' 
	Here we declare the plugin, so QGIS can find it and load it.
	This method should return an instance of the plugin class
	'''
    from what3words.plugin import W3WTools
    return W3WTools(iface)
