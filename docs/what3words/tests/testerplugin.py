# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#

# Tests for the QGIS Tester plugin. To know more see
# https://github.com/boundlessgeo/qgis-tester-plugin

import os

from qgis.utils import iface, plugins
from qgis.core import QgsMapLayerRegistry, QgsPoint

def functionalTests():
    try:
        from qgistester.test import Test
        from qgistester.utils import loadLayer
    except:
        return []

    def _loadLayer():
        layerfile = os.path.join(os.path.dirname(__file__), "w3w.shp")
        layer = loadLayer(layerfile)
        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def _setTool():
        plugins["what3words"].setTool()

    def _zoomTo():
        plugins["what3words"].zoomTo()

    w3wTest = Test("Test w3w")
    w3wTest.addStep("Load layer", _loadLayer)
    w3wTest.addStep("Select map tool", _setTool)
    w3wTest.addStep("Click within the layer polygon and verify that the computed 3 coords are 'healings.distorting.harsher'", isVerifyStep=True)
    w3wTest.addStep("Move map canvas", lambda: iface.mapCanvas().setCenter(QgsPoint(0, 0)))
    w3wTest.addStep("Open panel", _zoomTo)
    w3wTest.addStep("Enter 'healings.distorting.harsher' and click on 'zoom to'. Verify it zooms to the polygon layer")
    w3wTest.addStep("Click on 'remove marker' and verify it removes the marker")
    return [w3wTest]


def unitTests():
    _tests = []
    #add unit tests with _tests.extend(test_suite)
    return _tests
