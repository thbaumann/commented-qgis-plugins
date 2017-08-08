from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QCursor

from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.gui import QgsMapTool, QgsMessageBar
from qgis.utils import iface

from what3words.w3w import what3words
from qgiscommons.settings import pluginSetting
from qgiscommons.gui import execute

class W3WMapTool(QgsMapTool):
    '''
    A map tool that react to user clicks on the map canvas, and shows the w3w 
    address corresponding to the clicked location
    '''

    epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.setCursor(Qt.CrossCursor)
        apiKey = pluginSetting("apiKey")
        self.w3w = what3words(apikey=apiKey)

    def toW3W(self, pt):
        '''Transform coordinate from canvas CRS into EPSG:4326'''
        canvas = iface.mapCanvas()
        canvasCrs = canvas.mapSettings().destinationCrs()
        transform = QgsCoordinateTransform(canvasCrs, self.epsg4326)
        pt4326 = transform.transform(pt.x(), pt.y())
        
        try:
            w3wCoords = execute(self.w3w.reverseGeocode(pt4326.y(), pt4326.x()))["words"]
        except Exception as e :
            w3wCoords = None

        return w3wCoords

    def canvasReleaseEvent(self, e):
        '''
        This is the method that is called when the user clicks and release the 
        mouse button. All the logic to be performed upon user clicks should be 
        added here'''

        '''
        We get the point the user clicked on and get its coordinate in the 
        canvas CRS
        '''
        pt = self.toMapCoordinates(e.pos())

        '''We transform it into a w3w address'''
        w3wCoord = self.toW3W(pt)
        '''
        Show message depending on whether the coord was correctly converted
        '''
        if w3wCoord:
            iface.messageBar().pushMessage("what3words", "The 3 word address: '{}' has been copied to the clipboard".format(w3wCoord), level=QgsMessageBar.INFO, duration=6)
            clipboard = QApplication.clipboard()
            clipboard.setText(w3wCoord)
        else:
            iface.messageBar().pushMessage("what3words", "Could not convert the selected point to a 3 word address", level=QgsMessageBar.WARNING, duration=3)
