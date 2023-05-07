## nmap-wrapper

A simple wrapper around the nmap cli

### Installation

```
# Optional, but recommended: Create a virtual environment
cd my_project
python -m venv .venv
source .venv/bin/activate

# Install
pip install path/to/nmap_wrapper

# Run an example
python path/to/nmap_wrapper/examples/[example].py
```

### Usage

A modified example taken from `examples/`.

```python
from nmap_wrapper import nmap, AttrAlias, TagAlias, XMLElement

class HostTag(XMLElement):
    start = AttrAlias("starttime", int)
    end = AttrAlias("endtime", int)
    status = AttrAlias("status.state", str)


class PortScan(XMLElement):
    protocol = AttrAlias("scaninfo.protocol", str)
    num_services = AttrAlias("scaninfo.numservices", int)
    port_range = AttrAlias("scaninfo.services", str)
    all_info = TagAlias("scaninfo", XMLElement)
    hosts = TagAlias.list("host", HostTag)


hosts = "localhost 127.0.0.1"
x = PortScan.from_string(nmap(f"-p20-22 {hosts}"))
print(f"{x.protocol=}, {x.num_services=}, {x.port_range=}")  # x.protocol='tcp', x.num_services=3, x.port_range='20-22'
```

### Credits

This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.
