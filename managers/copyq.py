from __future__ import annotations

import json
import subprocess
from shutil import which

from lib import exec_get, pid_of
from managers.manager_base import ClipboardManager

client = "copyq"


class CopyQ(ClipboardManager):
    @classmethod
    def can_start(cls) -> bool:
        return bool(which(client))

    @classmethod
    def is_running(cls) -> bool:
        return bool(pid_of(client))

    @classmethod
    def is_enabled(cls) -> bool:
        # activated and configured to sync clipboard
        # The "Auto" option detection logic will disfavor copyq when not running because it will show as disabled
        return (
            cls.can_start()
            and cls.is_running()
            and exec_get(client, "eval", 'monitoring() && config("check_clipboard")')
            == "true"
        )

    @classmethod
    def get_history(cls) -> list[str]:
        # CopyQ uses QT's JS implementation for scripting, which doesn't support modern JS
        script = (
            "history = [];"
            "for (var ind = 0; ind < size(); ind += 1) {"
            "  var text = str(read(ind));"
            "  if (history.indexOf(text) === -1) history.push(text);"
            "};"
            "JSON.stringify(history)"
        )
        return json.loads(exec_get(client, "eval", script)) # type: ignore[no-any-return]

    @classmethod
    def start(cls) -> None:
        subprocess.Popen([client])

    @classmethod
    def add(cls, text: str) -> None:
        subprocess.run([client, "add", text], check=False)
        subprocess.run([client, "copy", text], check=False)
