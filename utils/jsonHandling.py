import json

def dumpJSON(fname,data):
    with open(fname, 'w') as filehandle:
        json.dump(data, filehandle)
    return 

def loadJSON(fname):
    with open(fname, 'r') as filehandle:
        data = json.load(filehandle)
        print (data)
    return data

def checkIfExists(fname):
    if os.path.exists(fname):
        data = loadJSON(fname)
    else: 
        data = {}
    return data