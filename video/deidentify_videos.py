#!/usr/bin/env python3

# deidentify_videos.py,v1.0

# Copyright (c) 2020 Thomas Ward <thomas@thomasward.com>
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
De-identifies a directory of videos (mp4 or avi) by optionally renaming
them with either a random UUID or sequentially named file (e.g.
video001.mp4, video002.mp4...videoNNN.mp4) then stripping excessive
metadata from the video file. A CSV file to translate video filename to
randomized filename is saved to deidentify_YYYYMMDDHHMM.log by default
(filled in with the date-time) or a user-specified LOGFILE. Requires
Python 3.6+, docopt python package, and ffmpeg installed.

Usage:
    deidentify_videos.py [-l LOGFILE] [-s] INDIR OUTDIR
    deidentify_videos.py [-l LOGFILE] [-m] INDIR OUTDIR
    deidentify_videos.py -h

Options:
    -h          Show this screen and exit.
    -l LOGFILE  User-specified file to write a csv of old,new filenames.
    -s          Output sequential videoNNN rather than uuid filenames.
    -m          Only strip metadata; do not randomize filenames.

Arguments:
    INDIR       Directory containing videos.
    OUTDIR      Directory in which to place de-identified videos.
"""
from datetime import datetime
import logging
from math import floor, log10
from pathlib import Path
import secrets
import subprocess
import sys
from uuid import uuid4

from docopt import docopt


def setup_log(log_filename=None):
    """Creates a log file to record original to randomized video names.
    If no filename is specified, will create a log file named
    'deidentify_log_YYYYMMDDHHMM.csv'"""

    if log_filename is None:
        log_filename = (
            "deidentify_log_" + datetime.now().strftime("%Y%m%d%H%M") + ".csv"
        )
    # over-writes pre-existing file rather than appending to an old one
    logging.basicConfig(
        filename=log_filename, filemode="w", level=logging.INFO, format="%(message)s"
    )
    # write CSV header
    logging.info("%s,%s", "original", "randomized")


def name_generator(uuid=False, prefix="", start=0, width=3):
    """Returns functions that generate names. If uuid is True, will
    return a function that generates uuid4s. Otherwise, will return a
    function to generate incrementing names with a prefix added to the
    incrementing numbers that start at 'start' and padded to be 'width'
    wide, eg prefix = "video" then video001, video002, etc."""

    def incrementing_name():
        nonlocal n, prefix, width
        n += 1
        return prefix + f"{n:0{width}}"

    def uuid_name():
        return uuid4().hex

    if uuid:
        return uuid_name

    # subtract 1 from start because incrementing name will increment it
    # by one before initial use
    n = start - 1
    return incrementing_name


def seq_width(num):
    """Returns one more than order of magnitude (base-10) for num which
    is equivalent to the number of digits-wide a sequential
    representation would need to be. E.g.: num = 103 return 3 so
    sequences would be 000, 001, ... 102, 103."""
    return floor(log10(num)) + 1


def shuffle(some_list):
    """Returns the items in some_list in shuffled order."""
    # do a defensive copy so that the original list doesn't get
    # consumed by the 'pop()'
    items = some_list.copy()
    while items:
        yield items.pop(secrets.randbelow(len(items)))


def randomize_paths(vid_paths, outdir, sequentialize):
    """Returns a dict of orig_name: random_name. When sequentialize is
    true, random_names will be like video000, video001, etc, otherwise
    returns a uuid4."""
    if sequentialize:
        generate_name = name_generator(prefix="video", width=seq_width(len(vid_paths)))
    else:
        generate_name = name_generator(uuid=True)
    orig_to_random = {}
    # shuffle the filenames so that sequentially generated filenames
    # don't mimic the order of the filenames in the input directory
    for orig_path in shuffle(vid_paths):
        randomized_path = Path(outdir).joinpath(generate_name() + orig_path.suffix)
        orig_to_random[orig_path] = randomized_path

    return orig_to_random


def transpose_paths(paths, outdir):
    """Returns dict mapping each path in paths to a path from joining
    outdir with the basename of path."""
    return {path: Path(outdir).joinpath(path.name) for path in paths}


def is_video_path(path):
    """Checks if path has a video extension and is a file."""
    vid_exts = (".mp4", ".avi")
    return path.suffix.casefold() in vid_exts and path.is_file()


def get_video_paths(vid_dir):
    """Yield files with video extensions in vid_dir"""
    return [path for path in Path(vid_dir).rglob("*") if is_video_path(path)]


def strip_metadata(input_vid, output_vid):
    """Strips metadata from input_vid and places stripped video in
    output_vid. If successful returns output_vid's path, otherwise
    returns 'FAILED'."""
    command = [
        "ffmpeg",
        # set input video
        "-i",
        input_vid,
        # select all video streams
        "-map",
        "0:v",
        # select all audio streams if present
        "-map",
        "0:a?",
        # just copy streams, do not transcode (much faster and lossless)
        "-c",
        "copy",
        # strip global metadata for the video container
        "-map_metadata",
        "-1",
        # strip metadata for video stream
        "-map_metadata:s:v",
        "-1",
        # strip metadata for audio stream
        "-map_metadata:s:a",
        "-1",
        # remove any chapter information
        "-map_chapters",
        "-1",
        # remove any disposition info
        "-disposition",
        "0",
        output_vid,
    ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as perr:
        print(f"ffmpeg failed to strip '{input_vid}' with output:")
        print(perr.stdout, "And error messages:", perr.stderr, sep="\n")
        print("Script will continue to process the other videos.")
        # File failed to process so delete it is ffmpeg made an
        # incomplete one
        if output_vid.is_file():
            output_vid.unlink()
        return "FAILED"

    return output_vid


def main():
    """Will strip metadata and optionally randomize filenames from a
    directory of videos."""
    args = docopt(__doc__)

    vid_paths = get_video_paths(args["INDIR"])
    outdir = Path(args["OUTDIR"])
    try:
        outdir.mkdir()
    except FileExistsError:
        print(f"OUTDIR {outdir} must not already exist. Aborting.")
        sys.exit(2)
    setup_log(args["-l"])

    if args["-m"]:
        vid_map = transpose_paths(vid_paths, outdir)
    else:
        vid_map = randomize_paths(vid_paths, outdir, args["-s"])

    for orig_path, new_path in vid_map.items():
        # strip metadata then save into the csv log file:
        # orig_path,output (either new_path or "FAILED" if it was not successful)
        logging.info("%s,%s", orig_path, strip_metadata(orig_path, new_path))


if __name__ == "__main__":
    main()
