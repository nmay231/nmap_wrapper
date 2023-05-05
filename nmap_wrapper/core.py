import shlex
import shutil
from typing import List

nmap_path = shutil.which("nmap")

if not nmap_path:
    raise FileNotFoundError("nmap command not found by shutil. Is it in your path?")


def nmap(args: str, xml=True) -> List[str]:
    prefix = "-oX -" if xml else ""
    return shlex.split(f"{nmap_path} {prefix} {args}")
