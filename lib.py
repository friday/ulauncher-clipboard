import logging
import subprocess
import sys
import gi
from distutils.spawn import find_executable as find_exec

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gdk, Gtk, Notify, GObject
from time import sleep


logger = logging.getLogger('ulauncher-clipboard')
Notify.init('ulauncher-clipboard-extension')


def exec_get(*args):
    return subprocess.check_output(list(args)).rstrip().decode('utf-8')

def try_or(function, args, fallback=None):
    try:
        return function(*args)
    except Exception:
        return fallback

def try_int(string, fallback=0):
    return try_or(int, [string, 10], fallback)

def pid_of(name):
    # Get the first pid (there may be many space-separated pids), and parse to int
    pids = try_or(exec_get, ['pidof', '-x', name], '').split(' ')
    return try_int(pids[0], None)

# Run each call in a new throwaway thread to escape Gtk.IconTheme.get_default() stupid cache
def get_theme_icon(name, size):
    getIconCode = "Gtk.IconTheme.get_default().lookup_icon('{}', {}, 0).get_filename()".format(name, size)
    return exec_get(sys.executable, '-c', "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print({})".format(getIconCode))

def set_clipboard(text):
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(text, -1)
    clipboard.store()
    GObject.timeout_add(25, Gtk.main_quit)
    Gtk.main()

def show_message(title, message, icon, expires=Notify.EXPIRES_NEVER, urgency=2):
    message = Notify.Notification.new(title, message, icon)
    message.set_timeout(expires)
    message.set_urgency(urgency)
    message.show()
    return message

def ensure_status(manager, attempts=0):
    running = manager.is_running()

    if not running:
        logger.info('Attempting to start manager %s', manager.name)
        if not manager.can_start() or attempts > 30:
            logger.warn('Could not start manager %s (%i attempts)', manager.name, 0)
            return False

        manager.start()
        sleep(0.05 * attempts)
        return ensure_status(manager, attempts + 1)

    is_enabled = manager.is_enabled()

    if not is_enabled:
        logger.warn('Clipboard manager %s is disabled', manager.name)

    return is_enabled
