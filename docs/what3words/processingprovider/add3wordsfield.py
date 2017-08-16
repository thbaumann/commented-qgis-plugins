# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QIcon

try:
    from qgis.core import  QGis
except ImportError:
    from qgis.core import  Qgis as QGis

from qgis.core import QgsVectorDataProvider, QgsField, QgsCoordinateReferenceSystem, QgsCoordinateTransform

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

from what3words.w3w import what3words
from qgiscommons.settings import pluginSetting

pluginPath = os.path.split(os.path.dirname(__file__))[0]


class Add3WordsFieldAlgorithm(GeoAlgorithm):

    '''
    An algorithm that takes a points layer and oututs the same layer but with 
    an additional field containing w3w adresses of points in the input layer.
    '''

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def processAlgorithm(self, progress):
        '''
        Here is where the algorithm functionality takes places. This method is 
        called when the algorithm is executed'''

        apik = pluginSetting("apiKey")
        if apik is None or apik == ""::
            '''
            When there is a problem in a Processing algorithm, a 
            GeoAlgorithmExecutionException should be raised.
            '''
             raise GeoAlgorithmExecutionException("what3words API key is not defined")

        '''
        Get value selected by user. It will always be a string with the path 
        to the layer source.
        '''
        filename = self.getParameterValue(self.INPUT)
        
        '''Convert it to a QGIS layer object'''
        layer = dataobjects.getObjectFromUri(filename)
        
        '''Some checking'''
        provider = layer.dataProvider()
        caps = provider.capabilities()
        if not (caps & QgsVectorDataProvider.AddAttributes):
            raise GeoAlgorithmExecutionException("The selected layer does not support adding new attributes.")

        '''
        Check if there is a field named '3WordAddr'. If it exists already, 
        we will overwrite its content. Otherwise, we create a new one.
        '''
        idxField = layer.fieldNameIndex("3WordAddr")
        if idxField == -1:
            provider.addAttributes([QgsField("3WordAddr", QVariant.String, "", 254, 0)])
            layer.updateFields()
            idxField = layer.fieldNameIndex("3WordAddr")

        w3w = what3words(apikey=apik)

        nFeat = layer.featureCount()
        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

        '''
        We use this object to convert point coords from the layer CRS into 
        EPSG:4326, which is needed to call the w3w service
        '''
        transform = QgsCoordinateTransform(layer.crs(), epsg4326)

        '''Iterate over features'''
        for i, feat in enumerate(layer.getFeatures()):
            progress.setPercentage(int(100 * i / nFeat))
            '''Get Coordinate in layer CRS'''
            pt = feat.geometry().vertexAt(0)
            try:
                '''Convert to 4326'''
                pt4326 = transform.transform(pt.x(), pt.y())
                '''Convert 4326 coord into w3w address'''
                threeWords = w3w.reverseGeocode(pt4326.y(), pt4326.x())["words"]
            except Exception as e:
                progress.setDebugInfo("Failed to retrieve w3w address for feature {}:\n{}".format(feat.id(), str(e)))
                threeWords = ""

            provider.changeAttributeValues({feat.id() : {idxField: threeWords}})

        self.setOutputValue(self.OUTPUT, filename)

    def defineCharacteristics(self):

        '''The syntax of the algorithm is defined here'''

        self.name = 'Add 3 word address field to points layer'
        self.i18n_name = self.name
        self.group = 'what3words tools'
        self.i18n_group = self.group

        '''
        The algorithm rquires just one parameter: the layer to which w3w 
        adresses will be added
        '''
        Only one parameter 
        self.addParameter(ParameterVector(self.INPUT,
                                          'Input layer', [ParameterVector.VECTOR_TYPE_POINT]))

        self.addOutput(OutputVector(self.OUTPUT, 'Output', True))

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, "icons", "w3w.png"))
