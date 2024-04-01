from __future__ import annotations

import logging
import subprocess

import gi

gi.require_versions({"Gdk": "3.0", "Gtk": "3.0"})
try:
    gi.require_version("Notify", "0.8")
except ValueError:
    gi.require_version("Notify", "0.7")


from gi.repository import Gdk, GObject, Gtk, Notify  # type: ignore[attr-defined]  # noqa: E402

logger = logging.getLogger("ulauncher-clipboard")
Notify.init("ulauncher-clipboard-extension")


def exec_get(*args: str) -> str:
    proc = subprocess.run([*args], check=True, capture_output=True, text=True)
    return proc.stdout.rstrip()


def parse_int(string: str, fallback: int = 0) -> int:
    try:
        return int(string, 10)
    except Exception:
        return fallback


def pid_of(name: str) -> int | None:
    # Get the first pid (there may be many space-separated pids), and parse to int
    try:
        return int(exec_get("pidof", "-x", name))
    except subprocess.CalledProcessError:
        return None


def set_clipboard(text: str) -> None:
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(text, -1)
    clipboard.store()
    GObject.timeout_add(25, Gtk.main_quit)
    Gtk.main()


def show_message(title: str, body: str, icon: str) -> Notify.Notification:
    message = Notify.Notification.new(title, body, icon)
    message.set_timeout(Notify.EXPIRES_NEVER)
    message.set_urgency(2)
    message.show()
    return message
