import logging
import subprocess
import cgi
from time import sleep
from distutils.spawn import find_executable as findExec
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction


logger = logging.getLogger('ulauncher-clipboard')

def tryOr(function, args, fallback=None):
    try:
        return apply(function, args)
    except Exception:
        return fallback

def tryInt(string, fallback=0):
    return tryOr(int, [string, 10], fallback)

def pidOf(name):
    # Get the first pid (there may be many space-separated pids), and parse to int
    pids = tryOr(subprocess.check_output, [['pidof', '-x', name]], '').strip().split(' ')
    return tryInt(pids[0], None)

def ensureStatus(manager, attempts=0):
    running = manager.isRunning()

    if not running:
        logger.info('Attempting to start manager %s', manager.name)
        if not manager.canStart() or attempts > 30:
            logger.warn('Could not start manager %s (%i attempts)', manager.name, 0)
            return False

        manager.start()
        sleep(0.05 * attempts)
        return ensureStatus(manager, attempts + 1)

    isEnabled = manager.isEnabled()

    if not isEnabled:
        logger.warn('Clipboard manager %s is disabled', manager.name)

    return isEnabled

def showStatus(status):
    return RenderResultListAction([ExtensionResultItem(
        name          = status,
        on_enter      = DoNothingAction(),
        highlightable = False
    )])

def entryAsResult(query, entry):
    entryArr = entry.strip().split('\n')
    context = []
    pos = 0

    if query:
        line = filter(lambda l: query in l.lower(), entryArr)[0]
        pos = entryArr.index(line)

    if pos > 0:
        line = entryArr[pos - 1].strip()
        if line:
            context.append('...' + line)

    context.append(entryArr[pos])

    if len(entryArr) > pos + 1:
        line = entryArr[pos + 1].strip()
        if line:
            context.append(line + '...')

    encoded = list(map(cgi.escape, context))

    return ExtensionSmallResultItem(
        icon     = 'edit-paste.png',
        name     = '\n'.join(encoded),
        on_enter = ExtensionCustomAction(entry)
    )