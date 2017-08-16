from builtins import range
import os
import fnmatch

'''
Different imports to allow the plugin to work correctly in different versions
of QGIS
'''
try:
    from qgis.core import  QGis
except ImportError:
    from qgis.core import  Qgis as QGis

if QGis.QGIS_VERSION_INT < 29900:
    from qgis.core import QgsMarkerSymbolV2, QgsSvgMarkerSymbolLayerV2
else:
    from qgis.core import QgsMarkerSymbol as QgsMarkerSymbolV2
    from qgis.core import QgsSvgMarkerSymbolLayer as QgsSvgMarkerSymbolLayerV2


def symbolForCode(code, size):
    '''
    This method returns the marker corresponding to a given MIL-STD-2525 code
    '''
    try:    
        '''Here we create the marker symbol instance'''    
        symbol = QgsMarkerSymbolV2()
        '''
        A symbol in QGIS, for all types of geometries (in this case it's a 
        point symbol), is composed of a set of symbol layers.
        The default symbol contains one default layer. We do not want it, so 
        we remove all the previous symbol layers.
        '''

        for i in range(symbol.symbolLayerCount()):
            symbol.takeSymbolLayer(0)

        '''
        Now we just take the different parts of the MIL-STD-2525 code and
        convert it into a symbol layer. Is symbol layer is created from a
        corresponding SVG file, and by adding all of the to the marker symbol, 
        we get the compound marker to use.
        '''
        echelonCode = code[3] + code[8:10]
        echelonLayer = getSymbolLayer('Echelon', echelonCode, size)
        if echelonLayer is not None:
            symbol.insertSymbolLayer(0, echelonLayer)
     
        amplifierCode = code[3] + code[8:10]
        amplifierLayer = getSymbolLayer('Amplifier', amplifierCode, size)
        if amplifierLayer is not None:
            symbol.insertSymbolLayer(0, amplifierLayer)
    
        hqtffdCode = code[3:6] + code[7]
        hqtffdLayer = getSymbolLayer('HQTFFD', hqtffdCode, size)
        if hqtffdLayer is not None:
            symbol.insertSymbolLayer(0, hqtffdLayer)

        ocaCode = code[2:7] + '2'
        ocaLayer = getSymbolLayer('OCA', ocaCode, size)
        if ocaLayer is not None:
            symbol.insertSymbolLayer(0, ocaLayer)

        mainCode = code[4:6] + code[10:16]
        mainLayer = getSymbolLayer('Appendices', mainCode, size)
        if mainLayer is not None:
            symbol.insertSymbolLayer(0, mainLayer)

        modifier1Code = code[4:6] + code[16:18] + '1'
        modifier1Layer = getSymbolLayer('Appendices', modifier1Code, size)
        if modifier1Layer is not None:
            symbol.insertSymbolLayer(0, modifier1Layer)

        modifier2Code = code[4:6] + code[18:20] + '2'
        modifier2Layer = getSymbolLayer('Appendices', modifier2Code, size)
        if modifier2Layer is not None:
            symbol.insertSymbolLayer(0, modifier2Layer)

        frameCode = '%s_%s_%s' % (code[2], code[3:6], code[0])
        frameLayer = getSymbolLayer('Frames', frameCode, size)
        if frameLayer is not None:
            symbol.insertSymbolLayer(0, frameLayer)

        if symbol.symbolLayerCount() == 0:
            symbol = None
    except Exception as e:
        symbol = None

    return symbol


def getSymbolLayer(folder, svg, size):
    '''
    Returns a symbol layer correspoding to a given filename
    '''
    svg = svg + '.svg'
    root = os.path.join(os.path.dirname(__file__), 'svg', folder)
    filepath = None
    '''
    Find the file in the folder where all subsymbol SVGs are stored, from the 
    passed filename.
    '''
    for base, dirs, files in os.walk(root):
        matching = fnmatch.filter(files, svg)
        if matching:
            filepath = os.path.join(base, matching[0])
            break
    '''
    Create the symbol layer from the SVG file
    '''
    if filepath is not None:
        symbolLayer = QgsSvgMarkerSymbolLayerV2()
        symbolLayer.setPath(filepath)
        '''
        This tells QGIS that the size is expressed in pixels, so the marker
        would be rendered at the same size in the screen for all zoom levels. 
        To have a marker that is rendered at a different size depending on the
        scale, you can use QgsSymbolV2.MapUnit as the size unit.
        '''
        symbolLayer.setSizeUnit(QgsSymbolV2.Pixel)
        symbolLayer.setSize(size)
        return symbolLayer
    else:
        return None


def getDefaultSymbol(size):
    symbol = QgsMarkerSymbolV2()
    symbolLayer = QgsSvgMarkerSymbolLayerV2()
    symbolLayer.setPath(
        os.path.join(os.path.dirname(__file__), 'svg', 'question.svg'))
    symbolLayer.setSizeUnit(QgsSymbolV2.Pixel)
    symbolLayer.setSize(size)
    symbol.insertSymbolLayer(0, symbolLayer)
    return symbol
