from __future__ import annotations
from typing import Union, Mapping

from src.EMVValues.TagMeaning import get_tag_meaning


class EmvTag:

    def __init__(self,
                 tag_display: str,
                 tag_value: str,
                 tag_name: str,
                 tag_children: Mapping[str, 'EmvTag'] = None):
        self.display = tag_display
        self.name = tag_name
        self.value = tag_value
        self.length = int(len(tag_value) / 2)
        self.children = {} if tag_children is None else tag_children
        self.meaning = get_tag_meaning(tag_display)

    def add_child(self, tag_map: Mapping[str, EmvTag]) -> None:
        self.children = {**self.children, **tag_map}

    def dump(self, depth, suppress_values=True) -> str:
        if len(self.children) > 0 and suppress_values:
            dump = (f"{'---' * depth}[{self.display:>4}]"
                    f"[{self.meaning:<48}]"
                    f"\n")
        else:
            dump = (f"{'- -' * depth}[{self.display:>4}]"
                    f"[{self.meaning:<48}]"
                    f"[{self.value}]\n")

        for tag_name in self.children:
            dump = (f'{dump}'
                    f'{self.children[tag_name].dump(depth + 1, suppress_values)}')
        return dump

    def __str__(self) -> str:
        return self.dump(0)

    def search_tag(self, tag_name: str) -> Union[None, 'EmvTag']:
        if self.name == tag_name:
            return self
        else:
            if tag_name in self.children:
                return self.children[tag_name]
        return None

    def __getitem__(self, key: str) -> Union[None, 'EmvTag']:
        if len(key.split(':')) == 1:
            key = key + ':1'
        return self.search_tag(key)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def display(self) -> str:
        return self._display

    @display.setter
    def display(self, display: str):
        self._display = display

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    @property
    def length(self) -> int:
        return self._length

    @length.setter
    def length(self, length: int):
        self._length = length

    @property
    def meaning(self) -> str:
        return self._meaning

    @meaning.setter
    def meaning(self, meaning: str):
        self._meaning = meaning

    @property
    def children(self) -> Mapping[str, 'EmvTag']:
        return self._children

    @children.setter
    def children(self, children: Mapping[str, 'EmvTag']):
        self._children = children

    def __eq__(self, other: EmvTag):
        return self.__str__() == other.__str__()

