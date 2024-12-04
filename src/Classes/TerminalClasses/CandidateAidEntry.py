from __future__ import annotations

from dataclasses import dataclass, field, InitVar

from src.Classes.EmvTag import EmvTag


@dataclass(eq=True, order=True)
class CandidateAidEntry:
    application_priority_indicator: str = field(init=False)
    aid: str = field(init=False)
    application_label: str = field(init=False)
    application_preferred_name: str = field(init=False)
    directory_entry: InitVar[EmvTag]

    def __post_init__(self, directory_entry: EmvTag):
        self.aid = directory_entry['4F'].value
        self.application_label = directory_entry['50'].value if directory_entry['50'] else ""
        self.application_priority_indicator = directory_entry['87'].value if directory_entry['87'] else ""
        self.application_preferred_name = directory_entry['9F12'].value if directory_entry['9F12'] else ""
