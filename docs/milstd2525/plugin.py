
from builtins import object

import os
import webbrowser

from qgis.PyQt.QtWidgets import QAction

'''
Different imports to allow the plugin to work correctly in different versions
of QGIS
'''
try:
    from qgis.core import  QGis
except ImportError:
    from qgis.core import  Qgis as QGis

if QGis.QGIS_VERSION_INT < 29900:
    from qgis.core import QgsRendererV2Registry, QgsApplication
else:
    from qgis.core import QgsRendererRegistry as QgsRendererV2Registry
    from qgis.core import QgsApplication

from qgis.gui import QgsEditorWidgetRegistry

from milstd2525.renderer import MilStd2525RendererMetadata
from milstd2525.sidcwidgetwrapper import SIDCWidgetWrapperFactory
from qgiscommons.gui import addHelpMenu, removeHelpMenu

class MilStd2525Plugin(object):
    def __init__(self, iface):
        self.iface = iface

        '''Create the renderer objects'''
        self._rendererMetadata = MilStd2525RendererMetadata()
        self._widgetWrapperFactory = SIDCWidgetWrapperFactory()

        '''
        and register them so they are shown when the user edits the layer
        symbology
        '''
        QgsRendererV2Registry.instance().addRenderer(self._rendererMetadata)
        QgsEditorWidgetRegistry.instance().registerWidget('SIDC code editor', self._widgetWrapperFactory)

    def initGui(self):
        addHelpMenu("GeoGig")

    def unload(self):
        '''Remove the renderer when the plugin is unloaded'''
        QgsRendererV2Registry.instance().removeRenderer('MilStd2525Renderer')

        removeHelpMenu("GeoGig")

