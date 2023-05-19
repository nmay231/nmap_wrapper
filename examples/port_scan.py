import datetime
from nmap_wrapper import nmap, AttrAlias, TagAlias, XMLElement


class PortTag(XMLElement):
    protocol = AttrAlias("protocol", str)
    port = AttrAlias("portid", int)
    status = AttrAlias("state.state", str)
    service = AttrAlias("service.name", str)


# utc time (as string) to datetime object
utc_timestamp = lambda s: datetime.datetime.utcfromtimestamp(int(s))


class HostTag(XMLElement):
    start = AttrAlias("starttime", utc_timestamp)
    end = AttrAlias("endtime", utc_timestamp)
    status = AttrAlias("status.state", str)
    ports = TagAlias.list("ports.port", PortTag)


class PortScan(XMLElement):
    protocol = AttrAlias("scaninfo.protocol", str)
    num_services = AttrAlias("scaninfo.numservices", int)
    port_range = AttrAlias("scaninfo.services", str)
    all_info = TagAlias("scaninfo", XMLElement)
    hosts = TagAlias.list("host", HostTag)


hosts = "127.0.0.1 example.com"
x = PortScan.from_string(nmap(f"-p20-22 {hosts}"))
print(f"{x.num_services=}, {x.port_range=}")
print(x)
