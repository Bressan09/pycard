# coding=utf-8
from __future__ import annotations

from typing import Union, Mapping

from Utils.EMVValues.TagMeaning import get_tag_meaning


class EmvTag:

    # noinspection PySameParameterValue
    def __init__(self, tag_name: str, tag_value: str, tag_children: Mapping[str, EmvTag] = None):
        self.name = tag_name
        self.value = tag_value
        self.length = int(len(tag_value) / 2)
        self.children = {} if tag_children is None else tag_children
        self.meaning = get_tag_meaning(tag_name)

    def add_child(self, tag_map) -> None:
        self._children = {**self._children, **tag_map}

    def dump(self, depth, suppress_values=True) -> str:
        if len(self._children) > 0 and suppress_values:
            dump = (f"{'---' * depth}[{self._name:>4}]"
                    f"[{self._meaning:<48}]"
                    f"\n")
        else:
            dump = (f"{'- -' * depth}[{self._name:>4}]"
                    f"[{self._meaning:<48}]"
                    f"[{self._value}]\n")

        for tagName in self._children:
            dump = (f'{dump}'
                    f'{self._children[tagName].dump(depth + 1, suppress_values)}')
        return dump

    def __str__(self) -> str:
        return self.dump(0)

    def search_tag(self, tag_name: str) -> Union[None, EmvTag]:
        if self._name == tag_name:
            return self
        else:
            for child in self._children:
                search = self._children[child].search_tag(tag_name)
                if search:
                    return self._children[child]
        return None

    def __getitem__(self, key: str):
        split = key.split(':')
        tag = split[0]
        length_split = len(split)
        try:
            returnable = self._children[tag]
        except KeyError:
            raise KeyError(
                (f"Children '{tag}' not found, "
                 f"existing children are: {self._children.keys()}"))
        if length_split == 2:
            method = split[1].upper()
            if method == 'T':
                return returnable.name
            elif method == 'V':
                return returnable.value
            elif method == 'L':
                return returnable.length
            else:
                raise KeyError(
                    (f'Invalid Method Argument "{method}" '
                     f'valid methods are: "T", "V" and "L"')
                    )
        elif length_split > 2:
            raise KeyError('Invalid key argument')

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

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
    def children(self) -> Mapping[str, EmvTag]:
        return self._children

    @children.setter
    def children(self, children: Mapping[str, EmvTag]):
        self._children = children
