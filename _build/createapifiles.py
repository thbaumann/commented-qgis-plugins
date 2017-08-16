from qgis import core, gui
from qgis.PyQt import QtCore, QtGui, QtWidgets
from collections import defaultdict
import inspect
import sip

classes = []
methods = defaultdict(list)
modules = [core, gui, QtCore, QtGui, QtWidgets]
for m in modules:
	for k in m.__dict__.keys():
	    v = m.__dict__[k]
	    if inspect.isclass(v):
	        classes.append(k)        
	        for k2, v2 in v.__dict__.iteritems():            
	            if  "sip.methoddescriptor" in str(type(v2)): 
	                methods[k2].append(k)

#methods = {k:v for k,v in methods.iteritems() if len(v) == 1}

import json
with open('/Users/volaya/github/commented-qgis-plugins/_build/classes.json', 'w') as outfile:
    json.dump(classes, outfile)
    
with open('/Users/volaya/github/commented-qgis-plugins/_build/methods.json', 'w') as outfile:
    json.dump(methods, outfile)
