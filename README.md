## nmap-wrapper

A simple wrapper around the nmap cli.

> Note: the [`nmap`](https://nmap.org/) cli must be installed to use this library.

### Installation

```
# Create a virtual environment (Highly recommended)
mkdir nmap_demo && cd nmap_demo
python -m venv .venv
source .venv/bin/activate # Active the venv for this shell session

# Install
pip install ../path/to/nmap_wrapper
# Or from git
pip install 'nmap_wrapper @ git+https://github.com/nmay231/nmap_wrapper@[TAG OR COMMIT]'


# Run an example
python ../path/to/nmap_wrapper/examples/[example].py
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


hosts = "127.0.0.1 www.example.com"
x = PortScan.from_string(nmap(f"-p20-22 {hosts}"))
print(f"{x.protocol=}, {x.num_services=}, {x.port_range=}")  # x.protocol='tcp', x.num_services=3, x.port_range='20-22'
```

### Credits

This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.
