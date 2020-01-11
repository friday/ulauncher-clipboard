import os
import subprocess
from lib import logger, execGet, findExec, pidOf


name = 'GPaste'
client = 'gpaste-client'
dataFile = '{}/.local/share/GPaste/history.xml'.format(os.path.expanduser('~'))

# Fall back on old lowercased GPaste directory.
if not os.path.isfile(dataFile):
    dataFile = dataFile.lower()

def canStart():
    return bool(findExec(client))

def isRunning():
    return bool(pidOf('gpaste-daemon'))

def isEnabled():
    return canStart() and execGet('gsettings', 'get', 'org.gnome.GPaste', 'track-changes') == 'true'

def start():
    subprocess.call([client, 'start'])

def add(text):
    subprocess.call([client, 'add', text])

def getHistory():
    # The only separator options are zero butes and line breaks, and line breaks are very likely to be in the clipboard,
    # Zero bytes are less likely, but would not be my first choice
    return execGet('sh', '-c', "{0} $({0} get-history) --raw --zero".format(client)).split('\x00')