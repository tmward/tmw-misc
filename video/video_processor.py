#!/usr/bin/env python3

# video_processor.py,v1.0.1

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
Takes a directory with multiple video files, concatenates them,
trims excess video from the start and end of the video,
strips excess metadata, and outputs a single video in an mp4
container. Requires ffprobe and ffmpeg installed.
"""

import argparse
from datetime import datetime
from functools import partial
import json
import os
from shutil import rmtree, which
import subprocess
import sys
from tempfile import mkdtemp
from uuid import uuid4

import pyask


vid_exts = (".avi", ".flv", ".m4v", ".mkv", ".mpg", ".mov", ".mp4", ".webm", ".wmv")
stderr = partial(print, file=sys.stderr)


def stderr_and_exit(*args, **kwargs):
    """Print error message to stderr then exit."""
    stderr(*args, **kwargs)
    sys.exit(2)


def parser():
    """Returns an argparse parser."""
    prsr = argparse.ArgumentParser(
        description="Combine videos in a directory into one, de-identified, video.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    prsr.add_argument(
        "-o",
        "--output",
        help="Output filename. If none provided, generates random filename.",
    )
    prsr.add_argument(
        "-l",
        "--no-log",
        default=False,
        help="Do not save json log file.",
        action="store_true",
    )
    prsr.add_argument(
        "-a",
        "--keep-audio",
        default=False,
        help="Keep audio in final video.",
        action="store_true",
    )
    prsr.add_argument(
        "-f",
        "--keep-format",
        default=False,
        help="Do not convert final video to mp4.",
        action="store_true",
    )
    prsr.add_argument(
        "-m",
        "--keep-metadata",
        default=False,
        help="Do not strip metadata from final video.",
        action="store_true",
    )
    prsr.add_argument(
        "-t",
        "--no-trim",
        default=False,
        help="Do not offer to trim the video.",
        action="store_true",
    )
    prsr.add_argument("directory", help="directory with videos")
    return prsr


def validate_args(args):
    """Validates args and returns them if all valid."""
    if not os.path.isdir(args.directory):
        stderr_and_exit(f"{args.directory} is not a directory. Exiting.")
    if args.output is not None:
        if os.path.exists(args.output):
            stderr_and_exit(f"{args.output} already exists. Exiting.")
        out_ext = os.path.splitext(args.output)[1]
        if out_ext not in vid_exts:
            stderr_and_exit("Output file must have a valid video extension. Exiting.")
        if not args.keep_format and out_ext != ".mp4":
            stderr_and_exit('Output file must have "mp4" extension. Exiting.')
    return args


def is_video(filename):
    """Checks if filename is a video."""
    return filename.casefold().endswith(vid_exts)


def run(commands):
    """
    Convenience wrapper around subprocess.run().
    Runs commands, returning stdout. Exits on error if it fails.
    """
    try:
        return subprocess.run(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding="utf-8",
        ).stdout
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f'"{" ".join(commands)}" failed:\n{err.stderr}') from err


def ffprobe(filename):
    """Call ffprobe on filename. Returns dict of ffprobe's output."""
    return json.loads(
        run(
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
            ]
        )
    )


def make_workdir(directory):
    """Makes temporary working directory in directory."""
    try:
        workdir = mkdtemp(dir=directory)
    except OSError as err:
        stderr_and_exit(
            f'Failed to make temporary working directory with error:\n"{err}"'
        )
    # return relative path as we later cd into "directory"
    return os.path.relpath(workdir, directory)


def make_ffmpeg_concat_file(videos, workdir):
    """Writes file with list of videos for ffmpeg concat to work."""
    concat_filesname = os.path.join(workdir, "files.txt")
    with open(concat_filesname, "w") as concat_files:
        for video in videos:
            concat_files.write(f"file '{os.path.join('..', video)}'\n")
    return concat_filesname


def concat(infiles, outfile, workdir):
    """
    Takes a list of string filenames for videos, concats with ffmpeg,
    and returns tuple of concated filename and number of videos
    concatenated. This requires videos to have same codec.
    """
    if len(infiles) == 1:
        return (infiles[0], 1)
    videos = pyask.which_items(
        infiles,
        "Which videos, in order, should be stitched together?",
        allow_repeats=False,
        default=", ".join(map(str, range(0, len(infiles)))),
    )
    run(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            make_ffmpeg_concat_file(videos, workdir),
            "-map",
            "0",
            "-c",
            "copy",
            outfile,
        ]
    )
    return (outfile, len(videos))


def get_trim_times():
    """Asks user for start and end trim times. Returns them in seconds."""
    while True:
        start = pyask.seconds("What time should trim start?")
        end = pyask.seconds("What time should trim end?")
        if start < end:
            return (start, end)
        print("Start time must come before end time. Try again.")


def trim(infile, outfile):
    """Trim video with ffmpeg. Returns tuple of filename and dict of trim times"""
    if not pyask.yes_no("Does the video need to be trimmed?", default="yes"):
        return (infile, {"start": 0, "end": None})
    start, end = get_trim_times()
    run(
        [
            "ffmpeg",
            # need -ss before -i for fast seeking
            "-ss",
            str(start),
            "-i",
            infile,
            "-t",
            str(end - start),
            # use all streams
            "-map",
            "0",
            # copy, so it's fast. not necessarily precise b/c splits on i-frames
            "-c",
            "copy",
            # make all output streams have positive timestamps (could
            # happen if audio split precise but had to split on later
            # i-frame)
            "-avoid_negative_ts",
            "1",
            outfile,
        ]
    )
    return (outfile, {"start": start, "end": end})


def remove_audio(infile, outfile):
    """Remove audio from video with ffmpeg."""
    run(
        [
            "ffmpeg",
            "-i",
            infile,
            # keep all streams
            "-map",
            "0",
            # except audio
            "-map",
            "-0:a",
            # copy, don't need to transcode
            "-c",
            "copy",
            outfile,
        ]
    )
    return outfile


def mp4(infile, outfile):
    """If needed, takes infile and remuxes/transcodes to mp4 outfile."""
    if infile[-4:].casefold() == ".mp4":
        return infile
    try:
        # try simple remux first
        run(
            [
                "ffmpeg",
                "-i",
                infile,
                # use all streams
                "-map",
                "0",
                "-c",
                "copy",
                outfile,
            ]
        )
    except RuntimeError as err:
        print(f"Remux failed with:\n{err}")
        print("Transcoding to h264 instead (this will take a while!).")
        run(
            [
                "ffmpeg",
                "-i",
                infile,
                # use all streams
                "-map",
                "0",
                "-c:v",
                # use h264 at nearly lossless conversion crf setting
                "libx264",
                "-preset",
                "slow",
                "-crf",
                "18",
                outfile,
            ]
        )
    return outfile


def strip_metadata(infile, outfile):
    """Strips metadata from infile and places stripped video in
    outfile. Returns outfile's path."""
    run(
        [
            "ffmpeg",
            # set input video
            "-i",
            infile,
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
            outfile,
        ]
    )
    return outfile


def save_json(obj, logname="log.json"):
    """Save obj to logname as json b/c python json.dump() doesn't add newline."""
    with open(logname, "w") as logfile:
        logfile.write(json.dumps(obj, indent=2))
        logfile.write("\n")


def current_datetime():
    """Returns string of current date and time."""
    return datetime.today().strftime("%Y%m%d%H%M")


def random_videoname(extension=".mp4", directory=None):
    videoname = uuid4().hex + extension
    if directory is not None:
        return os.path.join(directory, videoname)
    return videoname


def main():
    """Processes a directory of video files into a single mp4 video."""
    args = validate_args(parser().parse_args())
    workdir = make_workdir(args.directory)
    # gen random names for videos to live in temporary "workdir"
    next_name = partial(random_videoname, directory=workdir)
    os.chdir(args.directory)
    videos = [f for f in sorted(os.listdir()) if is_video(f)]
    if len(videos) == 0:
        stderr_and_exit(f"No video files found in '{os.getcwd()}'.")
    og_extension = os.path.splitext(videos[0])[1].casefold()
    final_video = args.output if args.output is not None else random_videoname()
    final_extension = os.path.splitext(final_video)[1].casefold()
    # need a default trim time
    trim_times = {"start": 0, "end": None}
    try:
        inprocess_video, video_count = concat(videos, next_name(og_extension), workdir)
        og_info = ffprobe(inprocess_video)
        if not args.no_trim:
            inprocess_video, trim_times = trim(inprocess_video, next_name(og_extension))
        if not args.keep_audio:
            inprocess_video = remove_audio(inprocess_video, next_name(og_extension))
        if not args.keep_format:
            inprocess_video = mp4(inprocess_video, next_name(".mp4"))
        if not args.keep_metadata:
            inprocess_video = strip_metadata(
                inprocess_video, next_name(final_extension)
            )
        os.rename(inprocess_video, final_video)
        final_info = ffprobe(final_video)
        if not args.no_log:
            save_json(
                {
                    "video_count": video_count,
                    "original": og_info,
                    "final": final_info,
                    "trim_times": trim_times,
                },
                logname="log_" + current_datetime() + ".json",
            )
    except (OSError, RuntimeError) as err:
        stderr_and_exit(err)
    rmtree(workdir)
    print(f'Final video saved as "{os.path.join(args.directory, final_video)}".')


if __name__ == "__main__":
    if not which("ffprobe"):
        stderr_and_exit("ffprobe not found")
    if not which("ffmpeg"):
        stderr_and_exit("ffmpeg not found")
    if sys.version_info <= (3, 6):
        stderr_and_exit("Requires Python 3.6+")
    main()
