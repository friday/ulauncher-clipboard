import subprocess
import json
from lib import logger, tryOr, findExec, pidOf


name = 'CopyQ'
client = 'copyq'

def canStart():
    return bool(findExec(client))

def isRunning():
    return bool(pidOf(client))

def isEnabled():
    # activated and configured to sync clipboard
    # The "Auto" option detection logic will disfavor copyq when not running because it will show as disabled
    return isRunning() and subprocess.check_output([client, 'eval', 'monitoring() && config("check_clipboard")']) == 'true\n'

def start():
    # Open and don't wait
    subprocess.Popen([client])

def getHistory():
    # CopyQ uses QT's JS implementation for scripting, which doesn't support modern JS
    script = "history = []; for (var ind = 0; ind < size(); ind += 1) { history.push(str(read(ind))); }; JSON.stringify(history)"
    return json.loads(subprocess.check_output([client, 'eval', script]))
