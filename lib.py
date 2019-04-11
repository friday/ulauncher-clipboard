import logging
import subprocess
import sys
import gi
import os

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gdk, Gtk, Notify
from time import sleep
from distutils.spawn import find_executable as findExec


logger = logging.getLogger('ulauncher-clipboard')
Notify.init('ulauncher-clipboard-extension')


def execGet(*args):
    return subprocess.check_output(list(args)).rstrip()

def tryOr(function, args, fallback=None):
    try:
        return apply(function, args)
    except Exception:
        return fallback

def tryInt(string, fallback=0):
    return tryOr(int, [string, 10], fallback)

def pidOf(name):
    # Get the first pid (there may be many space-separated pids), and parse to int
    pids = tryOr(execGet, ['pidof', '-x', name], '').split(' ')
    return tryInt(pids[0], None)

# Run each call in a new throwaway thread to escape Gtk.IconTheme.get_default() stupid cache
def getThemeIcon(name, size):
    getIconCode = "Gtk.IconTheme.get_default().lookup_icon('{}', {}, 0).get_filename()".format(name, size)
    return execGet(sys.executable, '-c', "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print({})".format(getIconCode))

def setClipboard(text):
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(text, -1)
    clipboard.store()

def showMessage(title, message, icon, expires=Notify.EXPIRES_NEVER, urgency=2):
    message = Notify.Notification.new(title, message, icon)
    message.set_timeout(expires)
    message.set_urgency(urgency)
    message.show()
    return message

def ensureStatus(manager, attempts=0):
    running = manager.isRunning()

    if not running:
        logger.info('Attempting to start manager %s', manager.name)
        if not manager.canStart() or attempts > 30:
            logger.warn('Could not start manager %s (%i attempts)', manager.name, 0)
            return False

        manager.start()
        sleep(0.05 * attempts)
        return ensureStatus(manager, attempts + 1)

    isEnabled = manager.isEnabled()

    if not isEnabled:
        logger.warn('Clipboard manager %s is disabled', manager.name)

    return isEnabled
