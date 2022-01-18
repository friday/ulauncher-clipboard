import subprocess
from lib import exec_get, find_exec, pid_of


name = 'GPaste'
client = 'gpaste-client'

def can_start():
    return bool(find_exec(client))

def is_running():
    return bool(pid_of('gpaste-daemon'))

def is_enabled():
    return can_start() and exec_get('gsettings', 'get', 'org.gnome.GPaste', 'track-changes') == 'true'

def start():
    subprocess.call([client, 'start'])

def add(text):
    subprocess.call([client, 'add', text])

def get_history():
    # The only separator options are zero bytes and line breaks.
    # Line breaks are very likely to be in the actual clipboard entries, so we can't use that.
    # Zero bytes are less likely, but would not be my first choice.
    return exec_get('sh', '-c', "{0} $({0} get-history) --raw --zero".format(client)).split('\x00')