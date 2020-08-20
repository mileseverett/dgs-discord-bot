import os
import random
import string
import json
import sys, traceback

from discord import Embed
from utils import jsonHandling

def getRoles(allRoles):
    roles = []
    for x in allRoles:
        roles.append(x.name)
    return roles

def createFolder(directory):
    if not os.path.exists(directory):
            os.makedirs(directory)
    return

