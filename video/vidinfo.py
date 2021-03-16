#!/usr/bin/env python3

# vidinfo.py,v1.0.0

# Copyright (c) 2021 Thomas Ward <thomas@thomasward.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
Outputs a csv with information on the container and video bitstream
formats (codecs) of videos in the specified directory. Requires ffprobe
installed.
"""

import argparse
import os
from shutil import which
import subprocess
import sys

def parser():
    """Returns an argparse parser."""
    parser = argparse.ArgumentParser(
        description="Collect video format/codec information.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--toplevel",
        action="store_true",
        default=False,
        help="Only analyze videos in directory, not its subdirectories.",
    )
    parser.add_argument(
        "-o", "--output", help="CSV output filename", default="vidinfo.csv"
    )
    parser.add_argument("directory", help="directory with videos")
    return parser


def valid_args(args):
    """Validates args."""
    if not os.path.isdir(args.directory):
        print(f"{args.directory} is not a directory. Exiting.", file=sys.stderr)
        return False
    if os.path.exists(args.output):
        print(f"{args.output} already exists. Exiting.", file=sys.stderr)
        return False
    return True


def main():
    args = parser().parse_args("asdf".split())
    if not valid_args(args):
        sys.exit(2)


if __name__ == "__main__":
    if which("ffprobe"):
        main()
    print("ffprobe not found", file=sys.stderr)
    sys.exit(2)
