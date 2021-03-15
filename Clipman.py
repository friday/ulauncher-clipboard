import subprocess
import json
from lib import logger, execGet, tryOr, findExec, pidOf

name = 'Clipman'
client = 'clipman'
pasteAgent = "wl-paste"
copyAgent = "wl-copy"

def canStart():
    return bool(findExec(client))

def isRunning():
    return bool(pidOf(pasteAgent))

def isEnabled():
    # We can't really know this.
    return True

def start():
    # Open and don't wait
    subprocess.Popen([pasteAgent, '-t', 'text', "--watch", client ,'store'])

def add(text):
    # manager is based on another clipboard program
    subprocess.call([copyAgent, text])

def getHistory():
    val=json.loads(execGet(client, 'show-history'))
    val.reverse()
    return val

