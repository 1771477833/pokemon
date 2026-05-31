"""对话系统。"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class DialogueSession:
    """逐行推进的对话会话。"""

    lines: list[str]
    index: int = 0
    speaker: str = ""
    on_finish: Callable[[], None] | None = None
    finished: bool = False

    @classmethod
    def from_npc(cls, name: str, lines: list[str], on_finish: Callable[[], None] | None = None) -> "DialogueSession":
        formatted = []
        for line in lines:
            if "：" in line or ":" in line:
                formatted.append(line)
            else:
                formatted.append(f"{name}：{line}")
        return cls(lines=formatted, speaker=name, on_finish=on_finish)

    @property
    def current(self) -> str:
        if self.finished or not self.lines:
            return ""
        return self.lines[self.index]

    @property
    def has_more(self) -> bool:
        return not self.finished and self.index < len(self.lines) - 1

    def advance(self) -> bool:
        """推进一行，返回是否仍在对话中。"""
        if self.finished:
            return False
        if self.index < len(self.lines) - 1:
            self.index += 1
            return True
        self.mark_finished()
        return False

    def skip_all(self) -> None:
        """取消键：直接结束对话。"""
        self.mark_finished()

    def mark_finished(self) -> None:
        self.finished = True

    def consume_callback(self) -> Callable[[], None] | None:
        """取出并清除结束回调（由 Game 在对话结束后调用）。"""
        cb = self.on_finish
        self.on_finish = None
        return cb
