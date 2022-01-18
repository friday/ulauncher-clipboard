import subprocess
from lib import execGet, findExec, pidOf


name = 'GPaste'
client = 'gpaste-client'

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
    # The only separator options are zero bytes and line breaks.
    # Line breaks are very likely to be in the actual clipboard entries, so we can't use that.
    # Zero bytes are less likely, but would not be my first choice.
    return execGet('sh', '-c', "{0} $({0} get-history) --raw --zero".format(client)).split('\x00')