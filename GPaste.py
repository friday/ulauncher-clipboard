import os
import subprocess
from xml.etree.ElementTree import parse as parseXML
from lib import logger, findExec, pidOf


name = 'GPaste'
client = 'gpaste-client'
dataFile = '{}/.local/share/gpaste/history.xml'.format(os.path.expanduser('~'))

def canStart():
    return bool(findExec(client))

def isRunning():
    return bool(pidOf('gpaste-daemon'))

def isEnabled():
    return canStart() and subprocess.check_output(['gsettings', 'get', 'org.gnome.GPaste', 'track-changes']) == 'true\n'

def start():
    subprocess.call([client, 'start'])

def getHistory():
    history = []
    # Load data from the xml file (using the GPaste CLI would be way too slow)
    for child in parseXML(dataFile).getroot():
        # Ignore non-text entries
        if child.attrib['kind'] == 'Text':
            history.append(child.getchildren()[0].text.encode('utf-8'))

    return history
