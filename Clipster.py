import os
import subprocess
import re
import urllib
from lib import logger, execGet, findExec, pidOf


name = 'Clipster'
# URL to download clipster if it's not installed
binUrl = 'https://raw.githubusercontent.com/mrichar1/clipster/master/clipster'
# The delimiter needs to be long and complicated to avoid being something you copied
delim = 'a8;bpy]rAM6XFOgT#:m9C{3Qj4WFLxAE@{?FL_Os_]e,b]i=ah;+0[vG,;yurpHW>j?oAImf3,<RlrEUA,uqYPVm^ti(+/)!cNAg'
# Get the path to the extension
extDir = os.path.dirname(os.path.realpath(__file__))
# We can't use the global binary since we can't control the Python version it runs
# When Ulauncher upgrades to Python 3 it'll likely work, or reverse the problem
client = '{}/{}'.format(extDir, 'clipster')

def canStart():
    # Should always be true considering ^ but still good to test
    return bool(findExec(client))

def isRunning():
    # Also must detect if global clipster is running, so don't use "client" variable
    return bool(pidOf('clipster'))

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

# Download and prepare binary
if not canStart():
    # If there's no local client, fetch it
    urllib.urlretrieve(binUrl, client)
    # Force it to use Python2 (otherwise it crashes if run from Ulauncher)
    # Using env in the shebang makes the process name "python2" instead of Clipster
    # I'm sure there's a better way, but until then...
    pythonBinary = execGet('sh', '-c',  'env python2 -c "import sys; sys.stdout.write(sys.executable)"')
    subprocess.call(['sed', '-i', '1s|.*|#\\!{}|'.format(pythonBinary), client])
    # Make it executable
    os.chmod(client, 0o755)
