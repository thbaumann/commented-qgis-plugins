
from __future__ import absolute_import

import os

from qgis.PyQt import uic

'''
Different imports to allow the plugin to work correctly in different versions
of QGIS
'''
try:
    from qgis.core import  QGis
except ImportError:
    from qgis.core import  Qgis as QGis

if QGis.QGIS_VERSION_INT < 29900:
    from qgis.core import QgsFeatureRendererV2, QgsRendererV2AbstractMetadata, QgsMarkerSymbolV2, QgsSymbolV2, QGis
    from qgis.gui import QgsRendererV2Widget, QgsFieldProxyModel
else:
    from qgis.core import QgsFeatureRenderer as QgsFeatureRendererV2
    from qgis.core import QgsRendererAbstractMetadata as QgsRendererV2AbstractMetadata
    from qgis.core import QgsMarkerSymbol as QgsMarkerSymbolV2
    from qgis.core import QgsSymbol as QgsSymbolV2
    from qgis.gui import QgsRendererWidget as QgsRendererV2Widget

from qgis.gui import QgsFieldProxyModel

from milstd2525.milstd2525symbology import symbolForCode, getDefaultSymbol


pluginPath = os.path.dirname(__file__)

'''
This loads the UI files dynamically, on the fly, so there is no need to 
compile ui files in advance.
'''
WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'milstd2525rendererwidgetbase.ui'))


class MilStd2525Renderer(QgsFeatureRendererV2):
    '''
    A renderer that sets the feature marker depending on the values from a 
    layer attribute, assuming that those values are MIL-STD-2525 codecs.
    '''
    def __init__(self, size=40, field=''):
        QgsFeatureRendererV2.__init__(self, 'MilStd2525Renderer')
        self.field = field
        self.size = size
        self._defaultSymbol = getDefaultSymbol(size)
        '''Cache symbols for better performance'''
        self.cached = {}

    def symbolForFeature(self, feature, context):
        '''
        Get the index of the attribute where MIL-STD-2525 codes are stored
        '''
        idx = feature.fieldNameIndex(self.field)
        if idx != -1:
            '''get the code from the attribute value'''
            code = feature.attributes()[idx]
            '''and create the symbol object'''
            if code not in self.cached:
                symbol = symbolForCode(code, self.size)
                if symbol is None:
                    self._defaultSymbol.setSize(self.size)
                    self.cached[code] = self._defaultSymbol
                else:
                    self.cached[code] = symbol.clone()
                    self.cached[code].startRender(self.context)
            self.cached[code].setSize(self.size)
            return self.cached[code]
        else:
            return self._defaultSymbol

    def startRender(self, context, fields):
        self.context = context
        for k,v in self.cached.items():
            v.startRender(context)
        self._defaultSymbol.startRender(context)

    def stopRender(self, context):
        for s in list(self.cached.values()):
            s.stopRender(context)
        self._defaultSymbol.stopRender(context)

    def usedAttributes(self):
        '''a list of the attributes used by the renderer'''
        return [self.field]

    def symbols(self, context):
        return list(self.cached.values())

    def clone(self):
        r = MilStd2525Renderer(self.size, self.field)
        r.cached = self.cached
        return r

    def save(self, doc):
        '''To allow saving the renderer properties to the QGIS project'''
        elem = doc.createElement('renderer-v2')
        elem.setAttribute('type', 'MilStd2525Renderer')
        elem.setAttribute('size', self.size)
        elem.setAttribute('field', self.field)
        return elem


class MilStd2525RendererWidget(QgsRendererV2Widget, WIDGET):
    '''
    A widget that is used to configure the renderer when it is selected in the 
    layer properties.
    '''
    def __init__(self, layer, style, renderer):
        super(MilStd2525RendererWidget, self).__init__(layer, style)
        self.setupUi(self)

        if renderer is None or renderer.type() != 'MilStd2525Renderer':
            fields = [f.name() for f in layer.dataProvider().fields()]
            self.r = MilStd2525Renderer(field = fields[0])
        else:
            self.r = renderer.clone()

        '''We populate the combobox with all the attributes of type string'''
        self.cmbField.setLayer(layer)
        self.cmbField.setFilters(QgsFieldProxyModel.String)

        '''Set the size in the size spinbox from the renderer value'''
        self.spnSize.setValue(self.r.size)

        '''connect widget signals to the corresponding methods'''
        self.cmbField.fieldChanged.connect(self.fieldChanged)
        self.spnSize.valueChanged[float].connect(self.sizeChanged)

    def sizeChanged(self, value):
        '''
        This method is called when the size box changes, and it modifies the 
        renderer size property.
        '''
        self.r.size = value

    def fieldChanged(self):
        '''
        This method is called when the field combo box changes, and it
        modifies the renderer field property.
        '''
        self.r.field = self.cmbField.currentText()

    def renderer(self):
        return self.r


class MilStd2525RendererMetadata(QgsRendererV2AbstractMetadata):
    def __init__(self):
        QgsRendererV2AbstractMetadata.__init__(
            self, 'MilStd2525Renderer', 'MIL-STD-2525 renderer')

    def createRenderer(self, element):
        return MilStd2525Renderer(int(element.attribute('size')), element.attribute('field'))

    def createRendererWidget(self, layer, style, renderer):
        return MilStd2525RendererWidget(layer, style, renderer)
