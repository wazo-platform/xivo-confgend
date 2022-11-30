#!/usr/bin/env python3

# simple utility script to transform an asterisk/ini-like conf file
# into a linear stream of namespaced option definitions, i.e. {section}.{option}={value}
# while conserving the original ordering of sections and options, allowing for easier semantic comparison

from typing import TextIO
from wazo_confgend.helpers.asterisk import asterisk_parser
import sys


def simplify_config_stream(file: TextIO):
    config = asterisk_parser(file)
    for section in config.sections():
        print("section:", section, file=sys.stderr)
        for (opt, val) in config.items(section):
            print("option:", opt, val, file=sys.stderr)
            yield (f"{section}.{opt}={val}")


if __name__ == "__main__":
    config_file = open(sys.argv[1]) if len(sys.argv) >= 2 else sys.stdin
    with config_file:
        print(config_file, file=sys.stderr)
        for abs_opt in simplify_config_stream(config_file):
            print(abs_opt)

        exit(0)
