def classFactory(iface):
	''' 
	Here we declare the plugin, so QGIS can find it and load it.
	This method should return an instance of the plugin class
	'''
    from milstd2525.plugin import MilStd2525Plugin
    return MilStd2525Plugin(iface)
