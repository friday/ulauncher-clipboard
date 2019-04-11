import subprocess
import Clipster
import CopyQ
import GPaste

from lib import logger, pidOf, tryInt, ensureStatus, findExec, getThemeIcon, setClipboard, showMessage
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction


clipboardManagers = [CopyQ, GPaste, Clipster]
sorter = lambda m: int("{}{}".format(int(m.isEnabled()), int(m.isRunning())))

def showStatus(status):
    return RenderResultListAction([ExtensionResultItem(
        name          = status,
        on_enter      = DoNothingAction(),
        highlightable = False
    )])

def formatEntry(icon, query, entry):
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

    return ExtensionSmallResultItem(
        icon     = icon,
        name     = '\n'.join(context),
        on_enter = ExtensionCustomAction(entry)
    )

def getManager(name):
    if name == 'Auto':
        contenders = filter(lambda m: m.canStart(), clipboardManagers);
        return sorted(contenders, key=sorter)[-1]

    return filter(lambda m: m.name == name, clipboardManagers)[0]

def setManager(name, extension):
    global manager
    logger.info('Loading ulauncher-clipboard manager: %s', name)
    manager = getManager(name)
    if not ensureStatus(manager):
        showMessage(
            'ulauncher-clipboard error',
            "Could not load {}. Make sure it's installed and enabled.".format(manager.name),
            getThemeIcon('dialog-error', 32)
        )

class PreferencesLoadListener(EventListener):
    def on_event(self, event, extension):
        extension.preferences.update(event.preferences)
        setManager(event.preferences['manager'], extension)


class PreferencesChangeListener(EventListener):
    def on_event(self, event, extension):
        if event.id == 'manager':
            setManager(event.new_value, extension)

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        maxLines = tryInt(extension.preferences['max_lines'], 20)
        icon = getThemeIcon('edit-paste', 32)
        query = (event.get_argument() or '').lower().encode('utf-8')

        if not ensureStatus(manager):
            return showStatus('Could not start {}. Please make sure you have it on your system and that it is not disabled.'.format(manager.name))

        try:
            history = manager.getHistory()

        except Exception as e:
            logger.error('Failed getting clipboard history')
            logger.error(e)
            return showStatus('Could not load clipboard history')

        # Filter entries if there's a query
        if query == '':
            matches = history[:maxLines]
        else:
            matches = []
            for entry in history:
                if len(matches) == maxLines:
                    break
                if query in entry.lower():
                    matches.append(entry)

        if len(matches) > 0:
            lines = 0
            results = []
            for entry in matches:
                result = formatEntry(icon, query, entry)
                # Limit to max lines and compensate for the margin
                lines += max(1, (result.get_name().count('\n') + 1) * 0.85)
                if maxLines >= lines:
                    results.append(result)

            return RenderResultListAction(results)

        return showStatus('No matches in clipboard history' if len(query) > 0 else 'Clipboard history is empty')

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        setClipboard(event.get_data())
        copyHook = extension.preferences['copy_hook']

        if copyHook:
            logger.info('Running copy hook: ' + copyHook)
            subprocess.Popen(['sh', '-c', copyHook])

class Clipboard(Extension):
    def __init__(self):
        super(Clipboard, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesLoadListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesChangeListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

if __name__ == '__main__':
    Clipboard().run()
