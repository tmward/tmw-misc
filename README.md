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

# Questions, comments, concerns
Start an issue/PR or contact me over your preferred medium on my
[contact](https://www.thomasward.com/contact/) page.
