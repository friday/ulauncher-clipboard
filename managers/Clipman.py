import os
import subprocess
import json
from shutil import which
from lib import exec_get, pid_of

name = 'Clipman'
client = 'clipman'
paste_agent = "wl-paste"
copy_agent = "wl-copy"

def can_start():
    return bool(which(client)) and bool(os.environ.get("WAYLAND_DISPLAY"))

def is_running():
    return bool(pid_of(paste_agent))

def is_enabled():
    # Clipman has no "state" where it's running but not recording your clipboard history.
    return True

def start():
    # Open and don't wait
    subprocess.Popen([paste_agent, '-t', 'text', "--watch", client ,'store', '-P'])

def add(text):
    # manager is based on another clipboard program
    subprocess.call([copy_agent], input=text.encode())

def get_history():
    val=json.loads(exec_get(client, 'show-history'))
    val.reverse()
    return val

