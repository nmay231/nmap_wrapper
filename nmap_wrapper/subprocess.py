import shlex
import shutil
from subprocess import PIPE, Popen
from typing import Sequence


def run_command_sync(command: Sequence[str]):
    """Runs the command in a subprocess and blocks until it completes.

    Returns the stdout of the subprocess."""

    proc = Popen(command, stdout=PIPE, stderr=PIPE, text=True)
    out, err = proc.communicate()
    return out


nmap_path = shutil.which("nmap")

if not nmap_path:
    raise FileNotFoundError("nmap command not found by shutil. Is it in your path?")


def nmap(args: str, xml=True) -> str:
    prefix = "-oX -" if xml else ""
    command = shlex.split(f"{nmap_path} {prefix} {args}")
    return run_command_sync(command)
