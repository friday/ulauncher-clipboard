import sys
import thread
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


# Simple clipboard manager which keep entries in memory as long as this manager is open
name = 'Fallback'
history = []
gtkClipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
_thread = 0

def canStart():
    return True

def isEnabled():
    return True

def isRunning():
    return bool(_thread)

def daemon(*args):
    gtkClipboard.connect('owner-change', ownerChangeListener)
    Gtk.main()

def ownerChangeListener(*args):
    text = gtkClipboard.wait_for_text()
    print((text, history))

    # Don't keep duplicates
    if text in history:
        history.remove(text)

    history.append(text)

def start():
    global _thread
    if not _thread:
        try:
            _thread = thread.start_new_thread(daemon, ())
        except:
           logger.error("Could not start Fallback manager")

def stop():
    print('@TODO: create me')

def getHistory():
    # Most recent should be first
    return history[::-1]
