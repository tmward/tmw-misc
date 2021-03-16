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
Outputs information on the container and video bitstream formats
(codecs) of videos in the specified directory. Requires ffprobe
installed.
"""

import argparse
import csv
from functools import partial
import json
import os
from shutil import which
import subprocess
import sys


def parser():
    """Returns an argparse parser."""
    prsr = argparse.ArgumentParser(
        description="Collect video format/codec information.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    prsr.add_argument(
        "-t",
        "--toplevel",
        action="store_true",
        default=False,
        help="Only analyze videos in directory, not its subdirectories.",
    )
    prsr.add_argument(
        "-f",
        "--format",
        default="json",
        help="Output format",
        choices=["csv", "json", "tsv"],
    )
    prsr.add_argument("-o", "--output", help="Output filename", default="-")
    prsr.add_argument("directory", help="directory with videos")
    return prsr


def valid_args(args):
    """Validates args."""
    if not os.path.isdir(args.directory):
        print(f"{args.directory} is not a directory. Exiting.", file=sys.stderr)
        return False
    if os.path.exists(args.output):
        print(f"{args.output} already exists. Exiting.", file=sys.stderr)
        return False
    return True


def is_video(filename):
    """Checks if filename is a video."""
    vid_exts = ("avi", "flv", "m4v", "mkv", "mpg", "mov", "mp4", "webm", "wmv")
    return filename.casefold().endswith(vid_exts)


def video_files(directory, toplevel=True):
    """Returns all toplevel files in directory."""
    for dirpath, _, files in os.walk(directory):
        for f in files:
            if is_video(f):
                yield os.path.join(dirpath, f)
        if toplevel:
            break


def ffprobe(filename):
    """Call ffprobe on filename. Returns dict of ffprobe's output."""
    try:
        return json.loads(
            subprocess.run(
                [
                    "ffprobe",
                    "-hide_banner",
                    "-select_streams",
                    "v",
                    "-show_entries",
                    "format=filename,format_name,duration:format_tags=:"
                    "stream=codec_name,width,height:stream_disposition=:"
                    "stream_tags=",
                    "-print_format",
                    "json",
                    filename,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=True,
                encoding="utf-8",
            ).stdout
        )
    except subprocess.CalledProcessError:
        print(f"ffprobe failed to process '{filename}'.", file=sys.stderr)
        return None


def tidy_streams(output):
    """Returns tidy dicts with info on each stream in ffprobe output."""
    for i, stream in enumerate(output["streams"]):
        yield {"stream_num": i, **stream, **output["format"]}


def save_json(dicts, fd):
    """Save dicts to fd as json."""
    for d in dicts:
        fd.write(json.dumps(d))
    fd.write("\n")


def save_csv(dicts, fd, sep=","):
    """Save dicts to fd as separated values using delimeter sep."""
    for i, d in enumerate(dicts):
        if i == 0:
            writer = csv.DictWriter(fd, fieldnames=d.keys(), delimiter=sep)
            writer.writeheader()
        writer.writerow(d)


def get_streams(directory, toplevel=False):
    """Fetches ffprobe output for video files in directory."""
    for f in video_files(directory, toplevel):
        output = ffprobe(f)
        if output is None:
            continue
        for stream in tidy_streams(output):
            yield stream


def main():
    """Parse args, call ffprobe on video files, and output."""
    args = parser().parse_args()
    if not valid_args(args):
        sys.exit(2)
    streams = get_streams(args.directory, args.toplevel)
    savefunc = {
        "json": save_json,
        "csv": save_csv,
        "tsv": partial(save_csv, sep="\t"),
    }
    # don't need to open/close file if user wants stdout aka "-"
    if args.output == "-":
        savefunc[args.format](streams, sys.stdout)
    else:
        with open(args.output, "w", newline="") as outfile:
            savefunc[args.format](streams, outfile)


if __name__ == "__main__":
    if not which("ffprobe"):
        print("ffprobe not found", file=sys.stderr)
        sys.exit(2)
    main()
