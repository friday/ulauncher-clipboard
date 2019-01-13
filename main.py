import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Gdk, Notify
from functools import partial
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent, ItemEnterEvent
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from lib import logger, pidOf, tryInt, ensureStatus, showStatus, entryAsResult, findExec
import Clipster
import CopyQ
import GPaste


clipboardManagers = [CopyQ, GPaste, Clipster]
sorter = lambda m: int("{}{}".format(int(m.isEnabled()), int(m.isRunning())))

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
        icon = Gtk.IconTheme.get_default().lookup_icon("dialog-error", 48, 0)

        Notify.init("ulauncher-clipboard-extension")
        message = Notify.Notification.new(
            "ulauncher-clipboard error",
            "Could not load {}. Make sure it's installed and enabled.".format(manager.name),
            icon.get_filename()
        )

        message.set_timeout(Notify.EXPIRES_NEVER)
        message.set_urgency(2)
        message.show()

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
                result = entryAsResult(query, entry)
                # Limit to max lines and compensate for the margin
                lines += max(1, (result.get_name().count('\n') + 1) * 0.85)
                if maxLines >= lines:
                    results.append(result)

            return RenderResultListAction(results)

        return showStatus('No matches in clipboard history' if len(query) > 0 else 'Clipboard history is empty')

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        text = event.get_data()
        copyHook = extension.preferences['copy_hook']

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()
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
