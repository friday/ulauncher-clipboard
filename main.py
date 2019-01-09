from functools import partial
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent
from lib import logger, pidOf, tryInt, ensureStatus, showStatus, entryAsResult, findExec
from actions import CopyAction, RenderResultListAction
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
        maxResults = tryInt(extension.preferences['max_results'], 6)
        contextLength = tryInt(extension.preferences['context_length'], 60)
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
            results = history[:maxResults]
        else:
            results = []
            for entry in history:
                if len(results) == maxResults:
                    break
                if query in entry.lower():
                    results.append(entry)

        # Get the handler for different keywords (only copy for now)
        handler = partial(entryAsResult, query, contextLength, CopyAction)

        if len(results) > 0:
            return RenderResultListAction(list(map(handler, results)))

        return showStatus('No matches in clipboard history' if len(query) > 0 else 'Clipboard history is empty')

class Clipboard(Extension):
    def __init__(self):
        super(Clipboard, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesLoadListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesChangeListener())

if __name__ == '__main__':
    Clipboard().run()
