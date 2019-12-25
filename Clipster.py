import os
import subprocess
import re
import urllib.request
from lib import logger, execGet, findExec, pidOf


name = 'Clipster'
# URL to download clipster if it's not installed
binUrl = 'https://raw.githubusercontent.com/mrichar1/clipster/master/clipster'
# The delimiter needs to be long and complicated to avoid being something you copied
delim = 'a8;bpy]rAM6XFOgT#:m9C{3Qj4WFLxAE@{?FL_Os_]e,b]i=ah;+0[vG,;yurpHW>j?oAImf3,<RlrEUA,uqYPVm^ti(+/)!cNAg'
client = 'clipster'

def canStart():
    # Should always be true considering ^ but still good to test
    return bool(findExec(client))

def isRunning():
    # Check if global clipster is running before the auto downloaded one
    return bool(pidOf('clipster') or pidOf('clipster_bin'))

def isEnabled():
    # We can't really know this. Users can configure clipster.ini not to sync the clipboard
    # This can't be easily tested though. The conf dir can vary
    return True

def start():
    if not isRunning():
        subprocess.Popen([client, '-d'])

def getHistory():
    # Clipster uses a json log file. However the default config is to defer/collect writes
    # so we have to call the client to get the latest
    return execGet(client, '--output', '--clipboard', '--number', '0', '--delim', delim).split(delim)

# Try finding global clipster binary
if not canStart():
    # Get the path to the extension
    extDir = os.path.dirname(os.path.realpath(__file__))
    # The name of the local binary must not be "clipster" to avoid an issue when down/upgrading between ulauncher v4/v5
    client = '{}/{}'.format(extDir, 'clipster_bin')
    # Try finding local binary
    if not canStart():
        # Download and prepare binary
        urllib.request.urlretrieve(binUrl, client)
        os.chmod(client, 0o755)
