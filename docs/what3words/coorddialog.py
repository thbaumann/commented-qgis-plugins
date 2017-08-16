from builtins import str

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QDockWidget,
                                 QLabel,
                                 QLineEdit,
                                 QPushButton,
                                 QHBoxLayout,
                                 QWidget,
                                 QApplication
                                )
from qgis.PyQt.QtGui import QCursor

from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform
                      )
from qgis.gui import QgsVertexMarker

from qgiscommons.settings import pluginSetting

class W3WCoordInputDialog(QDockWidget):
    def __init__(self, canvas, parent):
        self.canvas = canvas
        self.marker = None
        QDockWidget.__init__(self, parent)
        self.setAllowedAreas(Qt.TopDockWidgetArea)
        self.initGui()

    def setApiKey(self, apikey):
        self.w3w = what3words(apikey=apikey)

    def initGui(self):
        self.setWindowTitle("Zoom to 3 word address")
        self.label = QLabel('3 Word Address')
        self.coordBox = QLineEdit()
        
        '''
        When the button is pressed, we try to zoom to the coordinate entered
        by the user. That is done in the zoomToPressed method, but since this 
        is a method that might take a while to be executed (it connects 
        the w3w API), we use the 'execute' function in the qgiscommons 
        library, which will take care of changing the mouse pointer to an 
        hourglass until the method execution is finished.
        '''
        self.coordBox.returnPressed.connect(lambda: execute(self.zoomToPressed))
        self.zoomToButton = QPushButton("Zoom to")
        self.zoomToButton.clicked.connect(self.zoomToPressed)
        self.removeMarkerButton = QPushButton("Remove marker")
        self.removeMarkerButton.clicked.connect(self.removeMarker)
        self.removeMarkerButton.setDisabled(True)
        self.hlayout = QHBoxLayout()
        self.hlayout.setSpacing(6)
        self.hlayout.setMargin(9)
        self.hlayout.addWidget(self.label)
        self.hlayout.addWidget(self.coordBox)
        self.hlayout.addWidget(self.zoomToButton)
        self.hlayout.addWidget(self.removeMarkerButton)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setLayout(self.hlayout)
        self.setWidget(self.dockWidgetContents)

    def zoomToPressed(self):
        try:
            '''We convert the w3w address into a EPSG:4326 coord'''
            w3wCoord = str(self.coordBox.text()).replace(" ", "")
            json = self.w3w.forwardGeocode(w3wCoord)
            lat = float(json["geometry"]["lat"])
            lon = float(json["geometry"]["lng"])

            '''
            We convert the 4326 coord into a coord in the CRS of the canvas
            '''
            canvasCrs = self.canvas.mapSettings().destinationCrs()
            epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")
            transform4326 = QgsCoordinateTransform(epsg4326, canvasCrs)
            center = transform4326.transform(lon, lat)

            '''We zoom to that coord and set a marker'''
            self.canvas.zoomByFactor(1, center)
            self.canvas.refresh()
            if self.marker is None:
                self.marker = QgsVertexMarker(self.canvas)
            self.marker.setCenter(center)
            self.marker.setIconSize(8)
            self.marker.setPenWidth(4)

            '''Allow user to remove marker'''
            self.removeMarkerButton.setDisabled(False)
            
            self.coordBox.setStyleSheet("QLineEdit{background: white}")
        except Exception as e:
            self.coordBox.setStyleSheet("QLineEdit{background: yellow}")

    def removeMarker(self):
        self.canvas.scene().removeItem(self.marker)
        self.marker = None

    def closeEvent(self, evt):
        '''Remove marker when closing widget'''
        if self.marker is not None:
            self.removeMarker()
