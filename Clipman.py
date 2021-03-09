import subprocess
import json
from lib import logger, execGet, tryOr, findExec, pidOf

name = 'Clipman'
client = 'clipman'

def canStart():
    return bool(findExec(client))

def isRunning():
    return bool(pidOf(client))

def isEnabled():
    # We can't really know this.
    return True

def start():
    # Open and don't wait
    subprocess.call(['wl-paste', '-t', 'text', "--watch", 'clipman' ,'store'])

def add(text):
    # manager is based on another clipboard program
    subprocess.call(['wl-copy', text])

def getHistory():
    val=json.loads(execGet(client, 'show-history'))
    val.reverse()
    return val

