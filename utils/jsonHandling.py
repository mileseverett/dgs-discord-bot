import json
import os

def dumpJSON(fname, data):
    """
    Helper function to dump JSON data into a file

    Parameters:
    fname - String with the file path name to the JSON file
    data - data to add to JSON
    """
    with open(fname, 'w') as filehandle:
        json.dump(data, filehandle)
    return 

def loadJSON(fname):
    """
    Helper function to load JSON data from a file
    
    Parameters:
    fname - String with the file path name to the JSON file
    """
    if os.path.exists(fname):
        print ("File exists")
        with open(fname, 'r') as filehandle:
            data = json.load(filehandle)
            print (data)
    else:
        data = {}
    return data

