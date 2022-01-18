import subprocess
import json
from lib import exec_get, find_exec, pid_of

name = 'Clipman'
client = 'clipman'
pasteAgent = "wl-paste"
copyAgent = "wl-copy"

def can_start():
    return bool(find_exec(client))

def is_running():
    return bool(pid_of(pasteAgent))

def is_enabled():
    # We can't really know this.
    return True

def start():
    # Open and don't wait
    subprocess.Popen([pasteAgent, '-t', 'text', "--watch", client ,'store', '-P'])

def add(text):
    # manager is based on another clipboard program
    subprocess.call([copyAgent, text])

def get_history():
    val=json.loads(exec_get(client, 'show-history'))
    val.reverse()
    return val

