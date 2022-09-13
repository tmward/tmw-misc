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

# `outlook_emails.py`
Script that will take the clipboard contents
from the copied names and emails from an outlook recipients list and returns,
in the clipboard copy buffer, a two-column
tab-separated text of:

```
"name\temail"
"name2\temail2"
...
"name_last\temail_last"
```

which you can copy into a spreadsheet.

# R

Collection of scripts useful when programming in R.

## `pp_dd.R`
Script that will pretty print (pp), in markdown,
a data dictionary (dd) from a collection of dataframes/tibbles.
The data dictionary is in the standard three column format,
variable, class, description,
used in [TidyTuesday](https://github.com/rfordatascience/tidytuesday),
(e.g., [UN Votes data dictionary](https://github.com/rfordatascience/tidytuesday/blob/master/data/2021/2021-03-23/readme.md#data-dictionary)).

### Example

`mydfs.rds` is a named list of three dataframes.
By default, `pp_dd.R` prints with a markdown header level of 2
(so each table name is preceded with "##"):

```
$ ./pp_dd.R mydfs.rds

## `format_codecs`

|variable |class     |description |
|:--------|:---------|:-----------|
|`format` |character |            |
|`codec`  |character |            |

## `video_origins`

|variable      |class     |description |
|:-------------|:---------|:-----------|
|`video_id`    |character |            |
|`institution` |character |            |
|`recorder`    |character |            |
|`format`      |character |            |
|`codec`       |character |            |
|`file_total`  |integer   |            |
|`trim_start`  |integer   |            |

## `videos`

|variable   |class     |description |
|:----------|:---------|:-----------|
|`video_id` |character |            |
|`format`   |character |            |
|`codec`    |character |            |
|`width`    |integer   |            |
|`height`   |integer   |            |
|`duration` |numeric   |            |
|`complete` |logical   |            |

$ 
```

### Help

If you cannot remember the command line options,
help is a `-h` away!

```
$ ./pp_dd.R -h
Prints to standard output markdown to document R dataframes/tibbles.
Requires an RDS file that is either 1. A dataframe with columns
(name, df), with name, a character vector, and df, a list column holding
dataframes/tibbles or 2. a named list of dataframes.

It will output a markdown heading with the table name followed by a markdown
table with columns "name", "class" (eg., integer, character, etc), and
"description" (blank column for you to fill in).

Usage: tidy_tcga.R [-h] [-l LEVEL] INPUTRDS

Options:
    -h          Print this menu and exit.
    -l LEVEL    Markdown heading level, e.g. 1 is "#", 2 is "##" [default: 2].

    Arguments:
    INPUTRDS    R object saved in RDS format, either 2 column df
                or named list.
```

### Input

As input, it needs an RDS object that is either:

1. A named list of data frames (eg., `list("tbl1" = df(...), ..., "tbln" = df(...))`), the df for the example above was:
```
> str(named_list_of_my_dfs)
List of 3
 $ : tibble[,2] [18 × 2] (S3: tbl_df/tbl/data.frame)
  ..$ format: chr [1:18] "avi" "avi" "avi" "avi" ...
  ..$ codec : chr [1:18] "mpeg4" "h264" "hevc" "vp9" ...
 $ : tibble[,7] [539 × 7] (S3: tbl_df/tbl/data.frame)
  ..$ video_id   : chr [1:539] "vid1" "vid2" "vid3" "vid4" ...
  ..$ institution: chr [1:539] "Best Hospital" "Pretty Good Hospital" "Great Hospital" "Best Hospital" ...
  ..$ recorder   : chr [1:539] "camcorder" "smartphone" "camcorder" "smartphone" ...
  ..$ format     : chr [1:539] "avi" "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" ...
  ..$ codec      : chr [1:539] "mpeg4" "h264" "h264" "h264" ...
  ..$ file_total : int [1:539] 1 999 999 999 999 999 999 999 999 1 ...
  ..$ trim_start : int [1:539] 0 2002 166 131 17 102 176 540 0 0 ...
 $ : tibble[,7] [539 × 7] (S3: tbl_df/tbl/data.frame)
  ..$ video_id: chr [1:539] "vid1" "vid2" "vid3" "vid4" ...
  ..$ format  : chr [1:539] "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" ...
  ..$ codec   : chr [1:539] "mpeg4" "h264" "h264" "h264" ...
  ..$ width   : int [1:539] 1280 1920 1920 1920 1920 1280 720 1280 1280 1280 ...
  ..$ height  : int [1:539] 720 1080 1080 1080 1080 720 480 720 720 720 ...
  ..$ duration: num [1:539] 1488 5683 1779 3337 3843 ...
  ..$ complete: logi [1:539] TRUE TRUE TRUE TRUE TRUE TRUE ...
>
```

or

2. A two column data frame, `df(name = c("tbl1", ..., "tbln"), df = list(df1, ..., dfn))`
    - `name` is a character vectors of names
    - `df` is a list column holding the dataframes
    - A named list that would generate the example output is below:
```
> str(df_of_my_dfs)
tibble[,2] [3 × 2] (S3: tbl_df/tbl/data.frame)
 $ name: chr [1:3] "format_codecs" "video_origins" "videos"
 $ df  :List of 3
  ..$ : tibble[,2] [18 × 2] (S3: tbl_df/tbl/data.frame)
  .. ..$ format: chr [1:18] "avi" "avi" "avi" "avi" ...
  .. ..$ codec : chr [1:18] "mpeg4" "h264" "hevc" "vp9" ...
  ..$ : tibble[,7] [539 × 7] (S3: tbl_df/tbl/data.frame)
  .. ..$ video_id   : chr [1:539] "vid1" "vid2" "vid3" "vid4" ...
  .. ..$ institution: chr [1:539] "Best Hospital" "Best Hospital" "Best Hospital" "Best Hospital" ...
  .. ..$ recorder   : chr [1:539] "camcorder" "smartphone" "camcorder" "smartphone" ...
  .. ..$ format     : chr [1:539] "avi" "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" ...
  .. ..$ codec      : chr [1:539] "mpeg4" "h264" "h264" "h264" ...
  .. ..$ file_total : int [1:539] 1 999 999 999 999 999 999 999 999 1 ...
  .. ..$ trim_start : int [1:539] 0 2002 166 131 17 102 176 540 0 0 ...
  ..$ : tibble[,7] [539 × 7] (S3: tbl_df/tbl/data.frame)
  .. ..$ video_id: chr [1:539] "vid1" "vid2" "vid3" "vid4" ...
  .. ..$ format  : chr [1:539] "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" "mov,mp4,m4a,3gp,3g2,mj2" ...
  .. ..$ codec   : chr [1:539] "mpeg4" "h264" "h264" "h264" ...
  .. ..$ width   : int [1:539] 1280 1920 1920 1920 1920 1280 720 1280 1280 1280 ...
  .. ..$ height  : int [1:539] 720 1080 1080 1080 1080 720 480 720 720 720 ...
  .. ..$ duration: num [1:539] 1488 5683 1779 3337 3843 ...
  .. ..$ complete: logi [1:539] TRUE TRUE TRUE TRUE TRUE TRUE ...
>
```

### Output

`pp_dd.R` outputs to standard output.
If you want to save this as a file,
use standard command line output redirection
(`>` (to overwrite the specified file) or `>>`
(to append to the specified file)):

```
$ ./pp_dd.R -h 1 mydfs.rds > my_readme.md
```

Output is markdown.
There is a heading for each table
followed by a markdown table to describe each table.
This markdown table is styled in the usual three column format used by TidyTuesday:

1. `variable`: column name
2. `class`: type (e.g., integer, numeric, logical, etc.) of the column
3. `description`: blank column for you to fill in with your documentation.

You can control the heading level for the table name
(e.g., "#" versus "##") with the `-l` flag.
Default is 2, so "##".

### Required R packages

1. `docopt`
2. `dplyr`
3. `magrittr`
4. `purrr`
5. `tibble`
6. `knitr`

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

## `video_processor.py`

Python script that takes a directory with multiple video files
and combines them into a single video file.
The original video files are *not* modified.

### Overview

It performs the actions below.
Note, that all are performed by default,
but each can individually be turned off via command-line options:

1. Concatenates (joins) videos together, asking the user for their
   desired ordering of the videos.
2. Trims excess video from the start and end of the joined video by
   prompting the user for the timestamps where they want their final
   video to start and end.
3. Removes audio track if present.
4. Converts video to have an mp4 container, transcoding any audio/video
   codecs that are not compatible with an mp4 container in the process,
   if necessary. Output video codec, if transcoding is needed, is h264
   encoded with a constant rate factor of 18 to minimize loss during
   transcoding.
5. Strips excess metadata (read more on the dangers of video metadata
   [here](https://thomasward.com/video-metadata/))
6. Outputs:
    1. Single mp4 file in the video directory with either a random
       video name
       (32 hexadecimal digit [UUID4](https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)))
       or a user-specified video name.
    2. Log in json format that holds `ffprobe` information for the
       original videos (after they were concatenated) and the final
       output video.

It uses [`ffmpeg`](https://ffmpeg.org/) for the video processing.
It requires Python 3.6 or higher and my Python package
[pyask](https://pypi.org/project/pyask/).

### Example use

Video recorders often split a single "video" into multiple smaller videos.
For example, take the following directory full of videos:

```
$ ls example_video_directory
vid20190625-081711.avi  vid20190625-084933.avi  vid20190625-092155.avi
```

I can run `video_processor.py` to join them together,
in whatever order I would like,
then remove excess video from the starts and end,
remove the audio track,
convert them from an avi container to an mp4 container,
remove excess identifying metadata, and
output an mp4 with a random filename and
a json log file.
See below for output from an example run,
where I wanted to only use the 2nd and 3rd video in the directory,
and extract only time 1:00 to time 13:30:

```
$ ./video_processor.py example_video_directory
Available choices are:
(0) vid20190625-081711.avi
(1) vid20190625-084933.avi
(2) vid20190625-092155.avi
Which videos, in order, should be stitched together? (space/comma separated number(s)) [0, 1, 2] 1 2
Does the video need to be trimmed? (yes or no) [yes]
What time should trim start? (enter time in HH:MM:SS, MM:SS, or SS format) [] 1:00
What time should trim end? (enter time in HH:MM:SS, MM:SS, or SS format) [] 13:30
Final video saved as
"example_video_directory/b5cdf88919a344109311324a67ca4205.mp4".
$
```

You can see what the directory looks like after running:

```
$ ls example_video_directory
b5cdf88919a344109311324a67ca4205.mp4  log_202104291232.json
vid20190625-081711.avi  vid20190625-084933.avi  vid20190625-092155.avi
$
```

And the format of the log file:

```
$ cat example_video_directory/log_202104291232.json
{
  "original": {
    "programs": [],
    "streams": [
      {
        "codec_name": "mpeg4",
        "width": 1280,
        "height": 720
      }
    ],
    "format": {
      "filename": "tmpczwukxt2/71ef7566386042a280b640935cac60c5.avi",
      "format_name": "avi",
      "duration": "3508.966667"
    }
  },
  "final": {
    "programs": [],
    "streams": [
      {
        "codec_name": "mpeg4",
        "width": 1280,
        "height": 720
      }
    ],
    "format": {
      "filename": "b5cdf88919a344109311324a67ca4205.mp4",
      "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
      "duration": "750.000000"
    }
  }
}
```

### Help
Help is a `-h` away:

```
$ ./video_processor.py -h
usage: video_processor.py [-h] [-o OUTPUT] [-l] [-a] [-f] [-m] [-t] directory

Combine videos in a directory into one, de-identified, video.

positional arguments:
  directory             directory with videos

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output filename. If none provided, generates random
                        filename. (default: None)
  -l, --no-log          Do not save json log file. (default: False)
  -a, --keep-audio      Keep audio in final video. (default: False)
  -f, --keep-format     Do not convert final video to mp4. (default: False)
  -m, --keep-metadata   Do not strip metadata from final video. (default:
                        False)
  -t, --no-trim         Do not offer to trim the video. (default: False)
$
```

# Questions, comments, concerns
Start an issue/PR or contact me over your preferred medium on my
[contact](https://www.thomasward.com/contact/) page.
