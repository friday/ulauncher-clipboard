import subprocess
from lib import logger, try_int, ensure_status, set_clipboard, show_message
from managers import Clipman, Clipster, CopyQ, GPaste
from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

clipboard_managers = {m.name: m for m in [CopyQ, GPaste, Clipster, Clipman]}
sorter = lambda m: (m.can_start(), m.is_enabled(), m.is_running())


def format_entry(input, entry):
    entry_list = entry.strip().split('\n')
    context = []
    pos = 0

    if input:
        line = next(l for l in entry_list if input in l.lower())
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

    return Result(
        compact  = True,
        name     = '\n'.join(context),
        on_enter = ExtensionCustomAction(entry)
    )

def get_manager(name):
    if name == 'Auto':
        return sorted(clipboard_managers.values(), key=sorter)[-1]

    return clipboard_managers.get(name)

def set_manager(name):
    global manager
    logger.info('Loading ulauncher-clipboard manager: %s', name)
    manager = get_manager(name)
    if not ensure_status(manager):
        show_message(
            'ulauncher-clipboard error',
            f"Could not load {manager.name}. Make sure it's installed and enabled.",
            'dialog-error'
        )


class Clipboard(Extension):
    def __init__(self):
        super().__init__()
        set_manager(self.preferences['manager'])

    def on_preferences_update(self, id, value, previous_value):
        if id == "manager":
            set_manager(value)

    def on_input(self, input_text, trigger_id):
        max_lines = try_int(self.preferences['max_lines'], 20)

        if not ensure_status(manager):
            status = f'Could not start {manager.name}. Please make sure you have it on your system and that it is not disabled.'
            return [Result(name=status)]

        try:
            history = manager.get_history()

        except Exception as e:
            logger.error('Failed getting clipboard history')
            logger.error(e)
            return [Result(name='Could not load clipboard history')]

        # Filter entries if there's an input_text
        if input_text == '':
            matches = history[:max_lines]
        else:
            matches = []
            for entry in history:
                if len(matches) == max_lines:
                    break
                if input_text in entry.lower():
                    matches.append(entry)

        if len(matches) > 0:
            lines = 0
            for entry in matches:
                result = format_entry(input_text, entry)
                # Limit to max lines and compensate for the margin
                lines += max(1, (result.name.count('\n') + 1) * 0.85)
                if max_lines >= lines:
                    yield result

        return [Result(name='No matches in clipboard history' if len(input_text) > 0 else 'Clipboard history is empty')]

    def on_item_enter(self, text):
        copy_hook = self.preferences['copy_hook']

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

if __name__ == '__main__':
    Clipboard().run()
