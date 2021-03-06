#!/usr/bin/env Rscript

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

"
Prints to standard output markdown to document R dataframes/tibbles.
Requires an RDS file that is either 1. A dataframe with columns
(name, df), with name, a character vector, and df, a list column holding
dataframes/tibbles or 2. a named list of dataframes.

It will output a markdown heading with the table name followed by a markdown
table with columns \"name\", \"class\" (eg., integer, character, etc), and
\"description\" (blank column for you to fill in).

Usage: tidy_tcga.R [-h] [-l LEVEL] INPUTRDS

Options:
    -h          Print this menu and exit.
    -l LEVEL    Markdown heading level, e.g. 1 is \"#\", 2 is \"##\" [default: 2].

Arguments:
    INPUTRDS    R object saved in RDS format, either 2 column df or named list.
" -> doc

suppressPackageStartupMessages(library(docopt))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(magrittr))
suppressPackageStartupMessages(library(purrr))
suppressPackageStartupMessages(library(tibble))

description_df  <- function(df) {
    df %>%
        map_chr(class) %>%
        enframe(name = "variable", value = "class") %>%
        mutate(variable = paste0("`", variable, "`")) %>%
        mutate(description = "")
}

pp_table <- function(df, name, heading_level = 1) {
    cat(paste0("\n", strrep("#", heading_level), " `", name, "`"))
    print(knitr::kable(df))
}

opts <- docopt(doc)
input <- readRDS(opts$INPUTRDS)
heading_level <- suppressWarnings(as.integer(opts$l))

if (is.na(heading_level) || as.character(heading_level) != opts$l || heading_level < 1) {
    cat("LEVEL must be a positive integer", "\n")
    cat(doc, "\n")
    stop("LEVEL must be a positive integer", call. = FALSE)
}

if ("list" %in% class(input)) {
    input <- enframe(input, value = "df")
}

input %>%
    mutate(description = map(df, description_df)) %>%
    select(name, description) %>%
    deframe() %>%
    iwalk(pp_table, heading_level = heading_level)
