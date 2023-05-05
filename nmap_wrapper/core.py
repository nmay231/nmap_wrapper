import shlex
import shutil
import xml.etree.ElementTree as ET
from typing import List, TypeVar, Union

nmap_path = shutil.which("nmap")

if not nmap_path:
    raise FileNotFoundError("nmap command not found by shutil. Is it in your path?")


def nmap(args: str, xml=True) -> List[str]:
    prefix = "-oX -" if xml else ""
    return shlex.split(f"{nmap_path} {prefix} {args}")


T = TypeVar("T")


class XMLElement:
    @staticmethod
    def fromstring(string: str):
        return XMLElement(ET.fromstring(string))

    def __init__(self, wrapped: ET.Element):
        self._wrapped = wrapped

    def __getitem__(self, name: str) -> Union[str, "XMLElement"]:
        attr = self._wrapped.get(name)
        if attr is not None:
            return attr
        if (child := self._wrapped.find(name)) is not None:
            return XMLElement(child)
        raise KeyError(
            f"`{name}` is not an attribute or child of the `<{self._wrapped.tag}>` tag"
        )

    def get(self, name: str, alt: T = None) -> Union[str, "XMLElement", T, None]:
        try:
            return self[name]
        except KeyError:
            return alt
