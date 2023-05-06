import shlex
import shutil
import xml.etree.ElementTree as ET
from typing import Any, Callable, Generic, List, Optional, Type, TypeVar, Union, cast

nmap_path = shutil.which("nmap")

if not nmap_path:
    raise FileNotFoundError("nmap command not found by shutil. Is it in your path?")


def nmap(args: str, xml=True) -> List[str]:
    prefix = "-oX -" if xml else ""
    return shlex.split(f"{nmap_path} {prefix} {args}")


T = TypeVar("T")


class XMLElement:
    """A wrapper around xml.etree.ElementTree.Element that allows accessing
    XML attributes or children tags in a more convenient manner.

    Usage:
    ```python
    element = XMLElement.from_string(xml_string)
    print(element["child1"]["child2"]["attribute-name"])
    ```"""

    @classmethod
    def from_string(cls, string: str):
        return cls(ET.fromstring(string))

    def __init__(self, wrapped: ET.Element):
        self._wrapped = wrapped

    # TODO: If this code is run in Python 3.11+, it would be better to use typing.Self instead of XMLElement
    def __getitem__(self, name: str) -> Union[str, "XMLElement"]:
        attr = self._wrapped.get(name)
        if attr is not None:
            return attr
        if (child := self._wrapped.find(name)) is not None:
            return self.__class__(child)
        raise KeyError(
            f"`{name}` is not an attribute or child of the `<{self._wrapped.tag}>` tag"
        )

    def get(
        self, name: str, alt: Optional[T] = None
    ) -> Union[str, "XMLElement", T, None]:
        try:
            return self[name]
        except KeyError:
            return alt


# Is this overly complex and unnecessary? Perhaps. But it's useful.
class KeysAlias(Generic[T]):
    """Allows aliases of deeply nested xml properties and automatic casting from strings.

    Usage:
    ```python
    class ElementWithAliases(XMLElement):
        nmap_version = KeysAlias("version", str)
        verbosity = KeysAlias(["verbose", "level"], int)
        finished = KeysAlias("runstats.finished.timestr", dateutil.parser.parse)
        all_stats = KeysAlias("runstats")  # Keep as XMLElement

    element = ElementWithAliases.from_string(run_command_sync(nmap("-p 22")))

    print(element.nmap_version, element.verbosity, element.finished)
    print(type(element.all_stats) == ElementWithAliases)  # True
    ```"""

    def __init__(
        self,
        path: Union[str, List[str]],
        cast: Callable[[str], T] = XMLElement.from_string,
    ):
        self.path = path if isinstance(path, list) else path.split(".")
        if not self.path:
            raise ValueError(
                "path must be one or more keys in a list, or a string with keys separated by periods (.)"
            )
        self.cast = cast

    def __get__(self, obj: Optional[XMLElement], obj_type: Type[XMLElement]) -> T:
        if not obj:
            raise ValueError(f"Must call on an instance of {obj_type}")

        value: Any = obj
        for key in self.path:
            value = value[key]

        if self.cast == XMLElement.from_string:
            if isinstance(value, str):
                raise ValueError(
                    f"Value type of `{'.'.join(self.path)} = {value}` was left unspecified. "
                    "Pass a type like str or int, or write your own casting function."
                )
            return cast(T, value)
        elif isinstance(value, str):
            return self.cast(value)

        raise ValueError(
            f"The object at `{'.'.join(self.path)} = {value}` is an XML element, not an XML attribute."
        )
