from __future__ import annotations

import os
import subprocess
import urllib.request
from shutil import which

from lib import exec_get, logger, pid_of
from managers.manager_base import ClipboardManager

# URL to download clipster if it's not installed
binUrl = "https://raw.githubusercontent.com/mrichar1/clipster/master/clipster"
# The delimiter needs to be long and complicated to avoid being something you copied
delim = "a8;bpy]rAM6XFOgT#:m9C{3Qj4WFLxAE@{?FL_Os_]e,b]i=ah;+0[vG,;yurpHW>j?oAImf3,<RlrEUA,uqYPVm^ti(+/)!cNAg"
client = "clipster"


class Clipster(ClipboardManager):
    @classmethod
    def can_start(cls) -> bool:
        # which(client) should always be true considering, but still good to test
        return bool(which(client)) and not os.environ.get("WAYLAND_DISPLAY")

    @classmethod
    def is_running(cls) -> bool:
        # Check if global clipster is running before the auto downloaded one
        return bool(pid_of("clipster") or pid_of("clipster_bin"))

    @classmethod
    def is_enabled(cls) -> bool:
        # We can't really know this. Users can configure clipster.ini not to sync the clipboard
        # This can't be easily tested though. The conf dir can vary
        return True

    @classmethod
    def get_history(cls) -> list[str]:
        # Clipster uses a json log file. However the default config is to defer/collect writes
        # so we have to call the client to get the latest
        return exec_get(
            client, "--output", "--clipboard", "--number", "0", "--delim", delim
        ).split(delim)

    @classmethod
    def start(cls) -> None:
        subprocess.Popen([client, "-d"])

    @classmethod
    def add(cls, text: str) -> None:
        subprocess.run([client, "-c"], input=text.encode(), check=False)


# Try finding global clipster binary
if not Clipster.can_start():
    # Get the path to the extension
    extDir = os.path.dirname(os.path.realpath(__file__))
    # The name of the local binary must not be "clipster" to avoid an issue when down/upgrading between ulauncher v4/v5
    client = f"{extDir}/clipster_bin"
    # Try finding local binary
    if not which(client):
        try:
            # Download and prepare binary
            urllib.request.urlretrieve(binUrl, client)
            os.chmod(client, 0o755)
        except:  # noqa: E722
            logger.warning("Could not download clipster. Check your internet connection.")
