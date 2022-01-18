import os
import subprocess
import urllib.request
from shutil import which
from lib import exec_get, pid_of


name = 'Clipster'
# URL to download clipster if it's not installed
binUrl = 'https://raw.githubusercontent.com/mrichar1/clipster/master/clipster'
# The delimiter needs to be long and complicated to avoid being something you copied
delim = 'a8;bpy]rAM6XFOgT#:m9C{3Qj4WFLxAE@{?FL_Os_]e,b]i=ah;+0[vG,;yurpHW>j?oAImf3,<RlrEUA,uqYPVm^ti(+/)!cNAg'
client = 'clipster'

def can_start():
    # Should always be true considering ^ but still good to test
    return bool(which(client))

def is_running():
    # Check if global clipster is running before the auto downloaded one
    return bool(pid_of('clipster') or pid_of('clipster_bin'))

def is_enabled():
    # We can't really know this. Users can configure clipster.ini not to sync the clipboard
    # This can't be easily tested though. The conf dir can vary
    return True

def start():
    if not is_running():
        subprocess.Popen([client, '-d'])

def add(text):
    subprocess.run([client, '-c'], input=text, encoding='utf-8')

def get_history():
    # Clipster uses a json log file. However the default config is to defer/collect writes
    # so we have to call the client to get the latest
    return exec_get(client, '--output', '--clipboard', '--number', '0', '--delim', delim).split(delim)

# Try finding global clipster binary
if not can_start():
    # Get the path to the extension
    extDir = os.path.dirname(os.path.realpath(__file__))
    # The name of the local binary must not be "clipster" to avoid an issue when down/upgrading between ulauncher v4/v5
    client = '{}/{}'.format(extDir, 'clipster_bin')
    # Try finding local binary
    if not can_start():
        # Download and prepare binary
        urllib.request.urlretrieve(binUrl, client)
        os.chmod(client, 0o755)
