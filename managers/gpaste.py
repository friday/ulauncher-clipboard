from __future__ import annotations

import subprocess
from shutil import which

from lib import exec_get, pid_of
from managers.manager_base import ClipboardManager

client = "gpaste-client"


class GPaste(ClipboardManager):
    @classmethod
    def can_start(cls) -> bool:
        return bool(which(client))

    @classmethod
    def is_running(cls) -> bool:
        return bool(pid_of("gpaste-daemon"))

    @classmethod
    def is_enabled(cls) -> bool:
        return (
            GPaste.can_start()
            and exec_get("gsettings", "get", "org.gnome.GPaste", "track-changes")
            == "true"
        )

    @classmethod
    def get_history(cls) -> list[str]:
        return exec_get(
            "sh", "-c", f"{client} $({client} get-history) --raw --zero"
        ).split("\x00")

    @classmethod
    def start(cls) -> None:
        subprocess.run([client, "start"], check=False)

    @classmethod
    def add(cls, text: str) -> None:
        subprocess.run([client], input=text.encode(), check=False)
