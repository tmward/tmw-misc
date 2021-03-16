# Intro
This repository holds a collection of miscellaneous programs that I have
written. I tried to impose some semblance of organization into folders.
Description below for each script.

# `latex_svg.sh`
This script takes a user-specified single-line LaTeX formula and outputs a
stand-alone svg. It takes two arguments:

1. LaTeX formula (no surrounding $'s required, e.g., `\displaystyle\sum_{i=1}^{n} body`)
2. optional: filename for svg to save (default: formula.svg)

It requires latex and dvisvgm to be installed. Running:

```
$ ./latex_svg.sh "\displaystyle\sum_{i=1}^{n} body" sigma.svg
```

This will create a file, `sigma.svg`, that shows sum of body from the
sequence from i is one to n.

I mainly use it to generate LaTeX formulas into vector graphics that are
then used on my website.

# Videos

## `deidentify_videos.py`
`deidentify_videos.py` takes a directory of video files, strips excess
metadata from the videos, optionally randomizes the name, then places
them in a specified output directory. It requires Python 3.6 or higher,
the Python package [docopt](https://pypi.org/project/docopt/), and the
[FFmpeg](https://ffmpeg.org/) software package.

## `vidinfo.py`
Python script that leverages `ffprobe` to report the following information for videos location in a directory:

1. Filename
2. Video stream number (0-indexed. Most videos only have one video stream.)
3. Video codec name (standard name reported by ffmpeg/ffprobe)
4. Width (pixels)
5. Height (pixels)
6. Video container format (standard name reported by ffmpeg/ffprobe)
7. Duration (seconds)

It will report one item per video stream in the video file. Most videos only have one stream.

It requires `ffprobe` from the [FFmpeg](https://ffmpeg.org/) software package and Python 3.6 or higher.

I designed it to easily slot into any data pipeline,
so it can output in csv, tsv, or json formats.
By default it outputs to standard output
(and therefore works nice with pipes)
, but it will take an optional filename to output to as well.

Full help below:

```
$ ./vidinfo.py -h
usage: vidinfo.py [-h] [-t] [-f {csv,json,tsv}] [-o OUTPUT] directory

Collect video format/codec information.

positional arguments:
  directory             directory with videos

optional arguments:
  -h, --help            show this help message and exit
  -t, --toplevel        Only analyze videos in directory, not its
                        subdirectories. (default: False)
  -f {csv,json,tsv}, --format {csv,json,tsv}
                        Output format (default: json)
  -o OUTPUT, --output OUTPUT
                        Output filename (default: -)
```

# Questions, comments, concerns
Start an issue/PR or contact me over your preferred medium on my
[contact](https://www.thomasward.com/contact/) page.
