import subprocess
import sys

from event_collector import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "event_collector", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
