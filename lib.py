import logging
import subprocess
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

def getThemeIcon(name, size, fallback=None):
    try:
        logger.info('Trying to get icon for %s', name)
        desktopEnv = os.getenv('XDG_CURRENT_DESKTOP')
        if desktopEnv == 'Budgie:GNOME':
            desktopEnv = 'GNOME'

        # "Gtk.IconTheme.get_default()" can only get the Gnome theme, and doesn't update if the user switches it
        # This list is incomplete (part of why we need the try/except and fallback)
        iconThemeCmd = {
            'GNOME': 'gsettings get org.gnome.desktop.interface icon-theme',
            'X-Cinnamon': 'gsettings get org.cinnamon.desktop.interface icon-theme',
            'MATE': 'gsettings get org.mate.interface icon-theme',
            'xfce': 'xfconf-query -c xsettings -p /Net/IconThemeName',
        }[desktopEnv]

        if iconThemeCmd:
            iconThemeName = execGet('sh', '-c', iconThemeCmd).replace('\'', '')

        if iconThemeName:
            theme = Gtk.IconTheme.new()
            theme.set_custom_theme(iconThemeName)
            return theme.lookup_icon(name, size, 0).get_filename()

    except Exception:
        pass

    return fallback

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
