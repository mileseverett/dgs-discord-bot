import json
import os

def dumpJSON(fname, data):
    with open(fname, 'w') as filehandle:
        json.dump(data, filehandle)
    return 

def loadJSON(fname):
    print (fname)
    if os.path.exists(fname):
        print ("File exists")
        with open(fname, 'r') as filehandle:
            data = json.load(filehandle)
            print (data)
    else:
        data = {}
    return data

