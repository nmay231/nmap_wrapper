from subprocess import PIPE, Popen
from typing import Sequence


def run_command_sync(command: Sequence[str]):
    """Runs the command in a subprocess and blocks until it completes.

    Returns the stdout of the subprocess."""

    proc = Popen(command, stdout=PIPE, stderr=PIPE, text=True)
    out, err = proc.communicate()
    return out
