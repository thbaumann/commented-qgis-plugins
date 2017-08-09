from qgis import core, gui
from collections import defaultdict
import inspect
import sip

classes = []
methods = defaultdict(list)
modules = [core, gui]
for m in modules:
	for k in m.__dict__.keys():
	    v = m.__dict__[k]
	    if inspect.isclass(v):
	        classes.append(k)        
	        for k2, v2 in v.__dict__.iteritems():            
	            if  "sip.methoddescriptor" in str(type(v2)): 
	                methods[k2].append(k)

import json
with open('d:\\classes.json', 'w') as outfile:
    json.dump(classes, outfile)
    
with open('d:\\methods.json', 'w') as outfile:
    json.dump(methods, outfile)
