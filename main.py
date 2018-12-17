import logging
import os
import distutils.spawn
import subprocess
from functools import partial
from xml.etree.ElementTree import parse as parseXML
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

logger = logging.getLogger(__name__)
xmlPath = '{}/.local/share/gpaste/history.xml'.format(os.path.expanduser('~'))

def tryint(string, fallback):
    try:
        return int(string, 10)
    except Exception:
        return fallback

def showStatus(status):
    return RenderResultListAction([ExtensionResultItem(
        name          = status,
        on_enter      = DoNothingAction(),
        highlightable = False
    )])

def entryAsResult(query, contextLength, action, entry):
    formatted = entry.strip()
    multiline = '\n' in formatted
    entryData = formatted.split('\n', 1)
    title = entryData[0]
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

class Clipboard(Extension):
    def __init__(self):
        logger.info('Loading Clipboard Extension')
        super(Clipboard, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        max_results = tryint(extension.preferences['max_results'], 6)
        contextLength = tryint(extension.preferences['context_length'], 60)
        query = (event.get_argument() or '').lower()
        history = []

        try:
            # Load data from the xml file (using the GPaste CLI would be way too slow)
            for child in parseXML(xmlPath).getroot():
                history.append(child.getchildren()[0].text)

        except Exception as e:
            logger.error('Failed getting clipboard history')
            logger.error(e)
            return showStatus('Could not load clipboard history')

        # Filter entries if there's a query
        if query == '':
            results = history[:max_results]
        else:
            results = []
            for entry in history:
                if len(results) == max_results:
                    break
                if query in entry.lower():
                    results.append(entry)

        # Get the handler for different keywords (only copy for now)
        handler = partial(entryAsResult, query, contextLength, CopyToClipboardAction)

        if len(results) > 0:
            return RenderResultListAction(list(map(handler, results)))

        return showStatus('No matches in clipboard history' if len(query) > 0 else 'Clipboard history is empty')

if not distutils.spawn.find_executable('gpaste-client'):
    logger.error('gpaste-client not found. Cannot run GPaste extension')
elif __name__ == '__main__':
    # Start gpaste daemon if it's not already running
    subprocess.call(["gpaste-client", "start"])
    Clipboard().run()
