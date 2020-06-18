from utils import jsonHandling

def addBuffer()
    
    #load settings info
    if os.path.exists(fname):
        settings = jsonHandling.loadJSON(fname)
    else: 
        settings = {}