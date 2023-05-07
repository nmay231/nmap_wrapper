from nmap_wrapper import XMLElement


class MyXMLTag(XMLElement):
    pass


tag = MyXMLTag.from_string('<tag attr="value" />')
print(tag.get("attr"))  # value
