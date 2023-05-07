import xml.etree.ElementTree as ET
from typing import Callable, Generic, List, Optional, Type, TypeVar


def _recurse_xml_path(obj: ET.Element, path: List[str]) -> ET.Element:
    root_tag = obj.tag
    for i, key in enumerate(path):
        if (val := obj.find(key)) is None:
            raise KeyError(
                f"Tag <{obj.tag}> does not have child {key} (root tag <{root_tag}>, path={path[:i]})"
            )
        obj = val
    return obj


U = TypeVar("U", bound="XMLElement")


class XMLElement(ET.Element):
    """Inherit from this class to build a parser and use *Alias object to select certain attributes

    ```python
    class MyXMLTag(XMLElement):
        pass

    tag = MyXMLTag.from_string('<tag attr="value" />')
    print(tag.get("attr"))  # value
    ```

    Look in examples/ to see better use cases"""

    @classmethod
    def from_string(cls: Type[U], string: str) -> U:
        """Parse from an XML string"""
        return cls.new_from(ET.fromstring(string))

    @classmethod
    def new_from(cls: Type[U], other: ET.Element) -> U:
        """Create a new instance from any XMLElement-like object"""
        val = cls(other.tag)
        val.attrib = other.attrib
        val.extend(other)
        return val

    def __repr__(self) -> str:
        from textwrap import indent
        from itertools import chain
        import warnings

        attrs = []
        tags = []
        tag_lists = []
        for name, alias in self.__class__.__dict__.items():
            if isinstance(alias, AttrAlias):
                attrs.append(name)
            elif isinstance(alias, TagListAlias):
                tag_lists.append(name)
            elif isinstance(alias, TagAlias):
                tags.append(name)

        warnings.warn("!repr(object) is not the original XML!\n")
        attr = " ".join(f"{name}={getattr(self, name)!r}" for name in attrs)
        if not tags and not tag_lists:
            return f"<{self.tag} {attr} />"

        tags_ = (repr(getattr(self, tag)) for tag in tags)
        tags_list_ = map(repr, chain(*(getattr(self, tag) for tag in tag_lists)))
        children = indent("\n".join(chain(tags_, tags_list_)), "  ")
        return f"<{self.tag} {attr}>\n{children}\n<{self.tag} />"


T = TypeVar("T")


class AttrAlias(Generic[T]):
    """Supports aliasing attributes (optionally of children tags) directly on an XMLElement

    ```python
    class MyXMLTag(XMLElement):
        attribute = AttrAlias("attr", str)

    tag = MyXMLTag.from_string('<tag attr="value" />')
    print(tag.attribute, "::", type(tag.attribute))  # value :: <class 'str'>
    ```"""

    def __init__(self, path: str, cast: Callable[[str], T]):
        self.path = path.split(".")
        if not self.path:
            raise ValueError("path must be one or more keys separated by periods (.)")
        self.cast = cast

    def __get__(self, obj: Optional[ET.Element], obj_type: Type[ET.Element]) -> T:
        if obj is None:
            raise ValueError(f"Must call on an instance of {obj_type}")

        root_tag = obj.tag
        obj = _recurse_xml_path(obj, self.path[:-1])

        key = self.path[-1]
        if (attr := obj.get(key)) is None:
            raise KeyError(
                f"Tag <{obj.tag}> does not have child {key} (root tag <{root_tag}>, path={self.path})"
            )
        return self.cast(attr)


class TagListAlias(Generic[U]):
    """Supports aliasing (possibly nested) child tags directly on an XMLElement.

    ```python
    class MyXMLTag(XMLElement):
        hosts = TagAlias.list("hosts.host", XMLElement)

    tag = MyXMLTag.from_string('<parent> <hosts><host/><host/><hosts/> <parent/>')
    print(type(tag.hosts), len(tag.hosts))  # <class 'list'> 2
    ```"""

    def __init__(self, path: str, cast: Type[U]):
        if not path:
            raise ValueError("path must be one or more keys separated by periods (.)")
        self.path = path.split(".")

        if XMLElement not in cast.mro():
            raise ValueError(f"cast={cast} must be a subclass of {XMLElement.__name__}()")
        self.cast = cast

    def __get__(self, obj: Optional[XMLElement], obj_type: Type[XMLElement]) -> List[U]:
        if obj is None:
            raise ValueError(f"Must call on an instance of {obj_type}")

        val = _recurse_xml_path(obj, self.path[:-1])
        return [self.cast.new_from(child) for child in val.findall(self.path[-1])]


class TagAlias(Generic[U]):
    """Supports aliasing (possibly nested) child tags directly on an XMLElement

    ```python
    class OtherCustomTag(XMLElement): pass

    class MyXMLTag(XMLElement):
        child = TagAlias("a", OtherCustomTag)  # convert to custom tag or leave as default XMLElement
        nested = TagAlias("a.b", XMLElement) # Select nested children

    tag = MyXMLTag.from_string('<parent> <a><b/><a/> <parent/>')
    print(tag.child.tag, "::", tag.nested.tag)  # a :: b
    ```"""

    def __init__(self, path: str, cast: Type[U]):
        if not path:
            raise ValueError("path must be one or more keys separated by periods (.)")
        self.path = path.split(".")

        if XMLElement not in cast.mro():
            raise ValueError(f"cast={cast} must be a subclass of {XMLElement.__name__}()")
        self.cast = cast

    def __get__(self, obj: Optional[XMLElement], obj_type: Type[XMLElement]) -> U:
        if obj is None:
            raise ValueError(f"Must call on an instance of {obj_type}")

        return self.cast.new_from(_recurse_xml_path(obj, self.path))

    @staticmethod
    def list(path: str, cast: Type[U]) -> TagListAlias[U]:
        """See TagListAlias"""
        return TagListAlias(path, cast)
