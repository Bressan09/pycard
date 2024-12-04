from dataclasses import dataclass


@dataclass
class TerminalAcceptableAid:
    aid: str
    partial: bool
