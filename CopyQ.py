import subprocess
import json
from lib import logger, execGet, tryOr, findExec, pidOf


name = 'CopyQ'
client = 'copyq'

def canStart():
    return bool(findExec(client))

def isRunning():
    return bool(pidOf(client))

def isEnabled():
    # activated and configured to sync clipboard
    # The "Auto" option detection logic will disfavor copyq when not running because it will show as disabled
    return isRunning() and execGet(client, 'eval', 'monitoring() && config("check_clipboard")') == 'true'

def start():
    # Open and don't wait
    subprocess.Popen([client])

def getHistory():
    # CopyQ uses QT's JS implementation for scripting, which doesn't support modern JS
    script = "history = []; for (var ind = 0; ind < size(); ind += 1) {var text = str(read(ind)); if (history.indexOf(text) === -1) history.push(text); }; JSON.stringify(history)"
    return json.loads(execGet(client, 'eval', script))
