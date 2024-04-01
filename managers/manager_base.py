from __future__ import annotations

from abc import ABC, abstractmethod


class ClipboardManager(ABC):
    @classmethod
    @abstractmethod
    def can_start(self) -> bool:
        return False

    @classmethod
    @abstractmethod
    def is_running(self) -> bool:
        return False

    @classmethod
    @abstractmethod
    def is_enabled(self) -> bool:
        return False

    @classmethod
    @abstractmethod
    def get_history(self) -> list[str]:
        return []

    @classmethod
    @abstractmethod
    def start(cls) -> None:
        pass

    @classmethod
    @abstractmethod
    def add(cls, text: str) -> None:
        pass
