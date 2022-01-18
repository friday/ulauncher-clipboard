import subprocess

from lib import logger, try_int, ensure_status, get_theme_icon, set_clipboard, show_message
from managers import Clipman, Clipster, CopyQ, GPaste

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction


clipboard_managers = [CopyQ, GPaste, Clipster, Clipman]
sorter = lambda m: int("{}{}".format(int(m.is_enabled()), int(m.is_running())))

def show_status(status):
    return RenderResultListAction([ExtensionResultItem(
        name          = status,
        on_enter      = DoNothingAction(),
        highlightable = False
    )])

def format_entry(icon, query, entry):
    entry_list = entry.strip().split('\n')
    context = []
    pos = 0

    if query:
        line = next(l for l in entry_list if query in l.lower())
        pos = entry_list.index(line)

    if pos > 0:
        line = entry_list[pos - 1].strip()
        if line:
            context.append('...' + line)

    context.append(entry_list[pos])

    if len(entry_list) > pos + 1:
        line = entry_list[pos + 1].strip()
        if line:
            context.append(line + '...')

    return ExtensionSmallResultItem(
        icon     = icon,
        name     = '\n'.join(context),
        on_enter = ExtensionCustomAction(entry)
    )

def get_manager(name):
    if name == 'Auto':
        contenders = [m for m in clipboard_managers if m.can_start()]
        return sorted(contenders, key=sorter)[-1]

    for m in clipboard_managers:
        if m.name == name:
            return m

def set_manager(name, extension):
    global manager
    logger.info('Loading ulauncher-clipboard manager: %s', name)
    manager = get_manager(name)
    if not ensure_status(manager):
        show_message(
            'ulauncher-clipboard error',
            "Could not load {}. Make sure it's installed and enabled.".format(manager.name),
            get_theme_icon('dialog-error', 32)
        )

class PreferencesLoadListener(EventListener):
    def on_event(self, event, extension):
        extension.preferences.update(event.preferences)
        set_manager(event.preferences['manager'], extension)


class PreferencesChangeListener(EventListener):
    def on_event(self, event, extension):
        if event.id == 'manager':
            set_manager(event.new_value, extension)

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        max_lines = try_int(extension.preferences['max_lines'], 20)
        icon = 'edit-paste.png'
        query = (event.get_argument() or '').lower()

        if not ensure_status(manager):
            return show_status('Could not start {}. Please make sure you have it on your system and that it is not disabled.'.format(manager.name))

        try:
            history = manager.get_history()

        except Exception as e:
            logger.error('Failed getting clipboard history')
            logger.error(e)
            return show_status('Could not load clipboard history')

        # Filter entries if there's a query
        if query == '':
            matches = history[:max_lines]
        else:
            matches = []
            for entry in history:
                if len(matches) == max_lines:
                    break
                if query in entry.lower():
                    matches.append(entry)

        if len(matches) > 0:
            lines = 0
            results = []
            for entry in matches:
                result = format_entry(icon, query, entry)
                # Limit to max lines and compensate for the margin
                lines += max(1, (result.get_name().count('\n') + 1) * 0.85)
                if max_lines >= lines:
                    results.append(result)

            return RenderResultListAction(results)

        return show_status('No matches in clipboard history' if len(query) > 0 else 'Clipboard history is empty')

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        text = event.get_data()
        copy_hook = extension.preferences['copy_hook']

        # Prefer to use the clipboard managers own implementation
        if getattr(manager, 'add', None):
            logger.info("Adding to clipboard using clipboard manager's method")
            manager.add(text)
        else:
            logger.info("Adding to clipboard using fallback method")
            set_clipboard(text)

        if copy_hook:
            logger.info('Running copy hook: ' + copy_hook)
            subprocess.Popen(['sh', '-c', copy_hook])

class Clipboard(Extension):
    def __init__(self):
        super(Clipboard, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesLoadListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesChangeListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

if __name__ == '__main__':
    Clipboard().run()
