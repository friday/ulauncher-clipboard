from __future__ import annotations

import subprocess
from time import sleep

from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

from lib import logger, parse_int, set_clipboard, show_message
from managers import clipman, clipster, copyq, gpaste
from managers.manager_base import ClipboardManager

MAX_START_ATTEMPTS = 30
clipboard_managers: dict[str, type[ClipboardManager]] = {
    "CopyQ": copyq.CopyQ,
    "GPaste": gpaste.GPaste,
    "Clipster": clipster.Clipster,
    "Clipman": clipman.Clipman,
}


def ensure_status(manager, attempts=0):
    if not manager.is_running():
        logger.info("Attempting to start manager %s", manager.__name__)
        if not manager.can_start() or attempts > MAX_START_ATTEMPTS:
            logger.warning("Could not start manager %s (%i attempts)", manager.__name__, 0)
            return False

        manager.start()
        sleep(0.05 * attempts)
        return ensure_status(manager, attempts + 1)

    is_enabled = manager.is_enabled()

    if not is_enabled:
        logger.warning("Clipboard manager %s is disabled", manager.name)

    return is_enabled


def sorter(m: type[ClipboardManager]) -> tuple[bool, bool, bool]:
    return m.can_start(), m.is_enabled(), m.is_running()


def format_entry(text_input: str, entry: str) -> Result:
    entry_list = entry.strip().split("\n")
    context = []
    pos = 0

    if text_input:
        line = next(line for line in entry_list if text_input in line.lower())
        pos = entry_list.index(line)

    if pos > 0:
        line = entry_list[pos - 1].strip()
        if line:
            context.append("..." + line)

    context.append(entry_list[pos])

    if len(entry_list) > pos + 1:
        line = entry_list[pos + 1].strip()
        if line:
            context.append(line + "...")

    return Result(
        compact=True, name="\n".join(context), on_enter=ExtensionCustomAction(entry)
    )


def get_manager(name: str) -> type[ClipboardManager] | None:
    if name == "Auto":
        return sorted(clipboard_managers.values(), key=sorter)[-1]

    return clipboard_managers.get(name)


class Clipboard(Extension):
    manager: type[ClipboardManager]

    def __init__(self):
        super().__init__()
        self.set_manager(self.preferences["manager"])

    def set_manager(self, manager_name):
        logger.info("Loading ulauncher-clipboard manager: %s", manager_name)
        self.manager = get_manager(manager_name)
        if not ensure_status(self.manager):
            show_message(
                "ulauncher-clipboard error",
                f"Could not load {manager_name}. Make sure it's installed and enabled.",
                "dialog-error",
            )

    def on_preferences_update(self, pref_id, value, _previous_value):
        if pref_id == "manager":
            self.set_manager(value)

    def on_input(self, input_text, _trigger_id):
        max_lines = parse_int(self.preferences["max_lines"], 20)

        if not ensure_status(self.manager):
            status = (
                f"Could not start {self.manager.__name__}. "
                "Please make sure you have it on your system and that it is not disabled."
            )
            return [Result(name=status)]

        try:
            history = self.manager.get_history()

        except Exception as e:
            logger.error("Failed getting clipboard history")
            logger.error(e)
            return [Result(name="Could not load clipboard history")]

        # Filter entries if there's an input_text
        if input_text == "":
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
                lines += max(1, (result.name.count("\n") + 1) * 0.85)
                if max_lines >= lines:
                    yield result

        return [
            Result(
                name=(
                    "No matches in clipboard history"
                    if len(input_text) > 0
                    else "Clipboard history is empty"
                )
            )
        ]

    def on_item_enter(self, text):
        copy_hook = self.preferences["copy_hook"]

        # Prefer to use the clipboard managers own implementation
        if getattr(self.manager, "add", None):
            logger.info("Adding to clipboard using clipboard manager's method")
            self.manager.add(text)
        else:
            logger.info("Adding to clipboard using fallback method")
            set_clipboard(text)

        if copy_hook:
            logger.info("Running copy hook: " + copy_hook)
            subprocess.Popen(["sh", "-c", copy_hook])


if __name__ == "__main__":
    Clipboard().run()
