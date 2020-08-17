import os
import random
import string
import json
import sys, traceback

from discord import Embed
from utils import jsonHandling

def getRoles(ctx):
    roles = []
    for x in ctx.author.roles:
        roles.append(x.name)
    return roles