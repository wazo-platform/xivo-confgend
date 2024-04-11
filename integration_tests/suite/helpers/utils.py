import subprocess
from collections.abc import Iterable

DEFAULT_TIMEOUT = 10


def read_conf_file(path):
    with open(path) as file:
        conf = file.readlines()
        return list(normalize_lines(conf))


def run(cmd: list[str], timeout: int = DEFAULT_TIMEOUT) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, timeout=timeout
    )
    return result


def normalize_lines(line_stream: Iterable[str]):
    for line in line_stream:
        line = line.strip()
        if line:
            yield line
