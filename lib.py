import logging
import subprocess
from time import sleep
from distutils.spawn import find_executable as findExec
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

logger = logging.getLogger('ulauncher-clipboard')

def tryOr(function, args, fallback):
    try:
        return apply(function, args)
    except Exception:
        return fallback

def tryInt(string, fallback):
    return tryOr(int, [string, 10], fallback)

def pidOf(name):
    # Get the first pid (there may be many space-separated pids), and parse to int
    # Should probably be rewritten in a more "pythonic" way since lambdas can't do multiple lines/statements
    _pidOf = lambda name: int(subprocess.check_output(['pidof', name]).split(' ', 1)[0], 10)
    return tryOr(_pidOf, [name], False)

def ensureStatus(provider, attempts=0):
    running = provider.isRunning()

    if not running:
        logger.info('Attempting to start provider %s', provider.name)
        if not provider.canStart() or attempts > 30:
            logger.warn('Could not start provider %s (%i attempts)', provider.name, 0)
            return false

        provider.start()
        sleep(0.05 * attempts)
        return ensureStatus(provider, attempts + 1)

    isEnabled = provider.isEnabled()

    if not isEnabled:
        logger.warn('Provider %s is disabled', provider.name)

    return isEnabled

def showStatus(status):
    return RenderResultListAction([ExtensionResultItem(
        name          = status,
        on_enter      = DoNothingAction(),
        highlightable = False
    )])

def entryAsResult(query, contextLength, action, entry):
    formatted = entry.strip()
    multiline = '\n' in formatted
    title = formatted.split('\n', 1)[0]

    if multiline:
        pos = formatted.find(query)
        start = max(pos - contextLength, 0)
        end = min(pos + len(query) + contextLength, len(formatted))
        # Custom highlighting would be nice here but Ulauncher converts tags in the description to entities
        description = '{}{}{}'.format(
            '...' if start != 0 else '',
            formatted[start:end].strip(),
            '...' if end != len(formatted) else ''
        )

    return ExtensionResultItem(
        icon          = 'edit-paste.png',
        name          = title,
        description   = description if multiline else '',
        on_enter      = action(entry),
        # Ulauncher's highlighting is too limiting (turns multi-line to single-line and doesn't work on descriptions)
        highlightable = False
    )
