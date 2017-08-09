import os
import json
import shutil

with open('methods.json') as f:
    methods = json.load(f)
with open('classes.json') as f:
    classes = json.load(f)    

def createHtml():
    for folder in os.listdir(".."):
        src = os.path.join(os.path.abspath(".."), folder)
        dst = os.path.join(os.path.abspath(".."), "site", folder)        
        if os.path.isdir(src) and folder[0].isalpha():
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            for subdir, dirs, files in os.walk(dst):
                for f in files:
                    path = os.path.join(subdir, f)               
                    if path.endswith(".py"):
                        createHtmlFromPython(path)

with open("template.html") as f:
    template = f.read()

def createHtmlFromPython(path):
    with open(path) as f:
        code = f.read()
    
    for c in classes:
        code = code.replace(c, "<a href='http://qgis.org/api/2.18/class%s.html'>%s</a>" % (c,c))
    for k,v in methods.iteritems():
        code = code.replace(".%s(" % k, ".<a href='http://qgis.org/api/2.18/class%s.html'>%s</a>(" % (v[0],k))

    with open(path + ".html", "w") as f:
        f.write(template.replace("[code]", code))      


if __name__ == '__main__':  
    createHtml()