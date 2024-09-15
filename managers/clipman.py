from __future__ import annotations

import json
import os
import subprocess
from shutil import which

from lib import exec_get, pid_of
from managers.manager_base import ClipboardManager

client = "clipman"
paste_agent = "wl-paste"
copy_agent = "wl-copy"


class Clipman(ClipboardManager):
    @classmethod
    def can_start(cls) -> bool:
        return bool(which(client)) and bool(os.environ.get("WAYLAND_DISPLAY"))

    @classmethod
    def is_running(cls) -> bool:
        return bool(pid_of(paste_agent))

    @classmethod
    def is_enabled(cls) -> bool:
        # Clipman has no "state" where it's running but not recording your clipboard history.
        return True

    @classmethod
    def get_history(cls) -> list[str]:
        hist_chrono: list[str] = json.loads(exec_get(client, "show-history"))
        return [*reversed(hist_chrono)]

    @classmethod
    def start(cls) -> None:
        # Open and don't wait
        subprocess.Popen([paste_agent, "-t", "text", "--watch", client, "store", "-P"])

    @classmethod
    def add(cls, text: str) -> None:
        # manager is based on another clipboard program
        subprocess.run([copy_agent], input=text.encode(), check=False)
