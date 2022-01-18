import subprocess
import json
from shutil import which
from lib import exec_get, pid_of


name = 'CopyQ'
client = 'copyq'

def can_start():
    return bool(which(client))

def is_running():
    return bool(pid_of(client))

def is_enabled():
    # activated and configured to sync clipboard
    # The "Auto" option detection logic will disfavor copyq when not running because it will show as disabled
    return can_start() and is_running() and exec_get(client, 'eval', 'monitoring() && config("check_clipboard")') == 'true'

def start():
    # Open and don't wait
    subprocess.Popen([client])

def add(text):
    # For some reason adding the text to the copyq history and to the system clipboard are separate methods
    subprocess.call([client, 'add', text])
    subprocess.call([client, 'copy', text])

def get_history():
    # CopyQ uses QT's JS implementation for scripting, which doesn't support modern JS
    script = "history = []; for (var ind = 0; ind < size(); ind += 1) {var text = str(read(ind)); if (history.indexOf(text) === -1) history.push(text); }; JSON.stringify(history)"
    return json.loads(exec_get(client, 'eval', script))
