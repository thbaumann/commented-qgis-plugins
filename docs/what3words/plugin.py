from __future__ import absolute_import
from builtins import object

import os
import webbrowser

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.gui import QgsMessageBar
from qgis.core import QgsApplication
from qgis.utils import iface

from what3words.maptool import W3WMapTool
from what3words.coorddialog import W3WCoordInputDialog

from qgiscommons.gui import (addAboutMenu,
                             removeAboutMenu,
                             addHelpMenu,
                             removeHelpMenu)
from qgiscommons.settings import (readSettings,
                                  pluginSetting)
from qgiscommons.gui.settings import (addSettingsMenu,
                                    removeSettingsMenu)

#Processing might not be installed, so we only add the Processing provider if Processing is available
try:
    from processing.core.Processing import Processing
    from what3words.processingprovider.w3wprovider import W3WProvider
    processingOk = True
except:
    processingOk = False

class W3WTools(object):

    def __init__(self, iface):

        '''
        This plugin has tests that use the Tester plugin. If the plugin is 
        available and loaded, tests are added to it. Otherwise, they are 
        ignored
        '''
        try:
            from what3words.tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, "what3words")
        except:
            pass

        self.mapTool = None
        '''
        Create the Processing provider if Processing is availabel and loaded
        '''
        if processingOk:
            self.provider = W3WProvider()

        '''
        This must be added in the __init__ method, to tell the qgiscommons
        library that it has to load the settings for this plugin. It will find
        them automatically in a file named 'settings.json' in the plugin folder
        '''
        readSettings()

    def initGui(self):
        '''
        Here wew add the main menu entry, used to enable the map tool to 
        capture coordinates
        '''
        mapToolIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "w3w.png"))
        self.toolAction = QAction(mapToolIcon, "what3words map tool",
                                     iface.mainWindow())
        self.toolAction.triggered.connect(self.setTool)
        
        #checkable = true, so it indicates whether the maptool is active or not
        self.toolAction.setCheckable(True) 

        iface.addToolBarIcon(self.toolAction)
        iface.addPluginToMenu("what3words", self.toolAction)

        '''And here we add another tool to zoom to a w3w address'''
        zoomToIcon = QIcon(':/images/themes/default/mActionZoomIn.svg')
        self.zoomToAction = QAction(zoomToIcon, "Zoom to 3 word address",
                                     iface.mainWindow())
        self.zoomToAction.triggered.connect(self.zoomTo)
        iface.addPluginToMenu("what3words", self.zoomToAction)

        #Standard plugin menus provided by the qgiscommons library
        addSettingsMenu("what3words", iface.addPluginToMenu)
        addHelpMenu("what3words", iface.addPluginToMenu)
        addAboutMenu("what3words", iface.addPluginToMenu)

        '''
        This plugin uses a maptool. When another maptool is selected, our 
        plugin maptool will be disconnected, and we need to update the menu 
        entry, so it does not show itself as enabled. When the new tool is set, 
        it will fire a signal. We connect it to our unsetTool method, which 
        will handle this.
        '''
        iface.mapCanvas().mapToolSet.connect(self.unsetTool)

        '''
        We use a docked widget. We create it here and hide it, so when it is 
        called by the user, it is just set to visible and will be displayed in 
        its corresponding location in the app window.
        '''
        self.zoomToDialog = W3WCoordInputDialog(iface.mapCanvas(), iface.mainWindow())
        iface.addDockWidget(Qt.TopDockWidgetArea, self.zoomToDialog)
        self.zoomToDialog.hide()

        '''Add the Processing provider if Processing is availabel and loaded'''
        if processingOk:
            Processing.addProvider(self.provider)


    def zoomTo(self):
        apikey = pluginSetting("apiKey")
        if apikey is None or apikey == "":
            self._showMessage('what3words API key is not set. Please set it and try again.', QgsMessageBar.WARNING)
            return
        self.zoomToDialog.setApiKey(apikey)
        self.zoomToDialog.show()

    def unsetTool(self, tool):
        try:
            if not isinstance(tool, W3WMapTool):
                self.toolAction.setChecked(False)
        except:
            # ignore exceptions thrown when unloading plugin, since
            # map tool class might not exist already
            pass

    def setTool(self):
        apikey = pluginSetting("apiKey")
        if apikey is None or apikey == "":
            self._showMessage('what3words API key is not set. Please set it and try again.', QgsMessageBar.WARNING)
            return

        #Create the map tool if needed
        if self.mapTool is None:
            self.mapTool = W3WMapTool(iface.mapCanvas())
        #Change the menu item so it shows that the tool is active
        self.toolAction.setChecked(True)
        #Set the tool as the active map tool
        iface.mapCanvas().setMapTool(self.mapTool)

    def unload(self):
        '''
        Here we put all the actions to be performed when the plugin is unloaded
        '''
        #
        iface.mapCanvas().unsetMapTool(self.mapTool)
        
        '''Remove menus and buttons'''
        iface.removeToolBarIcon(self.toolAction)
        iface.removePluginMenu("what3words", self.toolAction)
        iface.removePluginMenu("what3words", self.zoomToAction)

        '''Remove qgiscommons menus'''
        removeSettingsMenu("what3words")
        removeHelpMenu("what3words")
        removeAboutMenu("what3words")

        '''Remove the main plugin widget'''
        iface.removeDockWidget(self.zoomToDialog)

        '''Remove processing provider'''
        if processingOk:
            Processing.removeProvider(self.provider)

        '''Remove tests'''
        try:
            from what3words.tests import testerplugin
            from qgistester.tests import removeTestModule
            removeTestModule(testerplugin, "what3words")
        except:
            pass


    def _showMessage(self, message, level=QgsMessageBar.INFO):
        iface.messageBar().pushMessage(
            message, level, iface.messageTimeout())
