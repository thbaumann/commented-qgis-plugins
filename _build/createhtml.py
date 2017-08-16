import os
import re
import json
import shutil
from collections import defaultdict

with open('methods.json') as f:
    methods = json.load(f)
with open('classes.json') as f:
    classes = json.load(f)    

def createHtml():
    docsfolder = os.path.join(os.path.abspath(".."), "docs")
    if os.path.exists(docsfolder):
        shutil.rmtree(docsfolder)
    os.makedirs(docsfolder)
    shutil.copy("index.html", os.path.join(docsfolder, "index.html"))
    for folder in os.listdir(".."):
        if folder == "docs":
            continue
        pyfiles = defaultdict(list)
        src = os.path.join(os.path.abspath(".."), folder)       
        if os.path.isdir(src) and folder[0].isalpha():
            dst = os.path.join(docsfolder, folder) 
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            for subdir, dirs, files in os.walk(dst):
                for f in files:
                    path = os.path.join(subdir, f)               
                    if path.endswith(".py"):
                        createHtmlFromPython(path)
                        pyfiles[subdir[len(dst):]].append(f)
            index = ["<h2>File list for %s plugin</h2>" % folder, '</div><div class="row"><ul>']
            for subdir, files in pyfiles.iteritems():
                if subdir:
                    index.append("<li>%s<ul>" % subdir)
                    for f in files:
                        index.append("<li><a href='./%s/%s.html'>%s</a>" % (subdir, f, f))
                    index.append("</ul>")
                else:
                    for f in files:
                        index.append("<li><a href='./%s.html'>%s</a>" % (f, f))
            index.append("</ul>")

            with open(os.path.join(dst, "%s.html" % folder), "w") as f:
                f.write(indextemplate.replace("[code]", "\n".join(index))) 


with open("codetemplate.html") as f:
    codetemplate = f.read()

with open("indextemplate.html") as f:
    indextemplate = f.read()

def createHtmlFromPython(path):
    with open(path) as f:
        code = f.read()
    
    for c in classes:
        folder = "qgispyapi" if c.startswith("Qgs") or c.startswith("Qgis") else "pyqt"
        code = re.sub(r"([^\w])%s([^\w])" % c, r"\1<a href='http://geoapis.sourcepole.com/%s/%s'>%s</a>\2" % (folder, c.lower(),c), code)
    for k,v in methods.iteritems():
        if len(v) == 1:
            clazz = (v[0] + ".") if v[0].startswith("Qgs") or v[0].startswith("Qgis") else ""
            folder = "qgispyapi" if v[0].startswith("Qgs") or v[0].startswith("Qgis") else "pyqt"
            code = code.replace(".%s(" % k, ".<a href='http://geoapis.sourcepole.com/%s/%s#%s%s'>%s</a>(" 
                                % (folder, v[0].lower(),clazz, k, k))
        else:
            dataContent = ["<ul>"]
            for option in v:
                folder = "qgispyapi" if option.startswith("Qgs") or option.startswith("Qgis") else "pyqt"
                clazz = (option + ".") if option.startswith("Qgs") or option.startswith("Qgis") else ""
                dataContent.append("<li><a href='http://geoapis.sourcepole.com/%s/%s#%s%s'>%s.%s()</a></li>" % (folder, option.lower(), clazz, k, option, k))
            dataContent.append("</ul>")
            code = code.replace(".%s(" % k, '.<a href="javascript://" data-toggle="popover" title="%s" data-content="%s">%s</a>(' % (k, "".join(dataContent), k))  
                                

    with open(path + ".html", "w") as f:
        f.write(codetemplate.replace("[code]", code))      


if __name__ == '__main__':  
    createHtml()