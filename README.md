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

# Questions, comments, concerns
Start an issue/PR or contact me over your preferred medium on my
[contact](https://www.thomasward.com/contact/) page.
