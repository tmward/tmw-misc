#!/usr/bin/env python3

"""
Take the clipboard contents copied from "My Cases" in Epic and produces a nicely
formated table, which it saves to the copy/paste buffer to use in a spreadsheet
software.
"""
import csv
from pprint import pprint
import re
import pyperclip


def tidy_patient_class(s):
    """Abbreviate patient class column."""
    class_to_abbrev = {
        "Post Procedure Recovery": "PPR",
        "Surgery Admit": "Admit",
        "Day Surgery": "Day",
    }
    if s in class_to_abbrev:
        return class_to_abbrev["s"]
    return s


def tidy_patient_name(s):
    """Remove 'preferred names' in quotes from names."""
    return re.sub(r"\".+?\" ", "", s)


def tidy_procedure(s):
    """Remove procedure code [NNNN] from procedure."""
    return re.sub(r" \[\d+\]", "", s)


def tidy_room(s):
    """Make MGW OR NN a more clear "WALTHMAM OR NN."""
    return re.sub(r"MGW", "WALTHAM", s)


def tidy_surgeons(s):
    """Only keep surgeon last name. When 2 surgeons, separate with /."""
    # Matches last name of either 1 or 2 surgeons
    # Will need to fix if 3+ surgeons encountered
    # surgeon names are "Last Names, First M; Last Names2, First2 M2"
    surgeon_regex = re.compile(r"(^.+?),.*?(; (.+?),.+)?$")
    surgeon_match = surgeon_regex.fullmatch(s).groups()
    if surgeon_match[2]:
        return surgeon_match[0] + "/" + surgeon_match[2]
    return surgeon_match[0]


def main():
    """Take OR table clipboard contents, format nicely, & put into clipboard buffer."""

    dat = pyperclip.paste().split("\r\n")[2:]

    final_dat = []
    ms_dat = []
    # useful to see if rows aren't full length due to mult surgeons
    ncols = 0
    for n, row in enumerate(dat):
        # add 1st row which is the headers
        if n == 0:
            final_dat.append(row)
            ncols = len(row.split("\t"))
        # skip blank rows
        elif not row.strip():
            continue
        # column with correct number of items
        elif len(row.split("\t")) == ncols:
            final_dat.append(row)
        # add not fitting rows to the "multi-surgeon" list
        # as when there are multi-surgeons, it copies and pastes them across
        # multiple lines
        else:
            ms_dat.append(row)

    # little janky, only works with 2 surgeons so far
    # merges the two surgeon two rows into one row
    n = 0
    while n < len(ms_dat):
        final_dat.append(ms_dat[n] + "; " + ms_dat[n + 1])
        n = n + 2

    # tidy
    tidiers = {
        "Patient Class": tidy_patient_class,
        "Patient Name": tidy_patient_name,
        "Procedure": tidy_procedure,
        "Residents/Fellows": lambda x: "",
        "Room": tidy_room,
        "Surgeons": tidy_surgeons,
        "Time": str,
    }
    reader = csv.DictReader(final_dat, dialect="excel-tab")
    final_tidied_dat = []
    for row in reader:
        if row["Progress Status"] == "Add On":
            row["Room"] = "Add On"
        new_row = {}
        for k, v in row.items():
            if k in tidiers:
                new_row[k] = tidiers[k](v)
        final_tidied_dat.append(new_row)

    # copy pastable
    columns = [
        "Room",
        "Time",
        "Patient Name",
        "Surgeons",
        "Procedure",
        "Patient Class",
        "Residents/Fellows",
    ]
    final_data = ["\t".join(columns)]
    for r in sorted(final_tidied_dat, key=lambda r: r["Room"] + r["Time"]):
        final_data.append("\t".join(r[c] for c in columns))
    pyperclip.copy("\n".join(final_data))


if __name__ == "__main__":
    main()
