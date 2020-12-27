import os
import random
import string
import json
import sys, traceback

from discord import Embed
from utils import jsonHandling

def getRoles(allRoles):
    """
    Helper function to get all unique roles
    """
    roles = []
    for x in allRoles:
        roles.append(x.name)
    return roles

def createFolder(directory):
    """
    Helper function to create a folder (generally for JSON data)
    """
    if not os.path.exists(directory):
            os.makedirs(directory)
    return

