import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from functools import partial
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent, ItemEnterEvent
from lib import logger, pidOf, tryInt, ensureStatus, showStatus, entryAsResult, findExec
from actions import RenderResultListAction
import CopyQ
import GPaste


providers = [CopyQ, GPaste]
sorter = lambda p: int("{}{}{}".format(int(p.canStart()), int(p.isEnabled()), int(p.isRunning())))

def getProvider(name):
    if name == 'Auto':
        return sorted(providers, key=sorter)[-1]

    return filter(lambda p: p.name == name, providers)[0]


def setProvider(name):
    global provider
    logger.info('Loading ulauncher-clipboard provider: %s', name)
    provider = getProvider(name)
    ensureStatus(provider)

class PreferencesLoadListener(EventListener):
    def on_event(self, event, extension):
        extension.preferences.update(event.preferences)
        setProvider(event.preferences['provider'])

class PreferencesChangeListener(EventListener):
    def on_event(self, event, extension):
        if event.id == 'provider':
            setProvider(event.new_value)

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        maxLines = tryInt(extension.preferences['max_lines'], 20)
        query = (event.get_argument() or '').lower().encode('utf-8')

        if not ensureStatus(provider):
            return showStatus('Could not start {}. Please make sure you have it on your system and that it is not disabled.'.format(name))

        try:
            history = provider.getHistory()

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
