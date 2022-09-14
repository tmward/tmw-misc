#!/usr/bin/env python3

"""
Take the clipboard contents copied from "My Cases" in Epic and produces a nicely
formated table, which it saves to the copy/paste buffer to use in a spreadsheet
software.
"""
import csv
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
        return class_to_abbrev[s]
    return s


def tidy_patient_name(s):
    """Remove "preferred names" from names."""
    return re.sub(r"\".+?\" ", "", s)


def tidy_procedure(s):
    """Remove procedure code [NNNN] from procedure."""
    return re.sub(r" \[\d+\]", "", s)


def tidy_room(s):
    """Make MGW OR NN a more clear "WALTHMAM OR NN."""
    return re.sub(r"MGW", "WALTHAM", s)


def tidy_surgeons(s):
    """Only keep surgeon last name. When 2+ surgeons, separate with /."""
    # surgeon names are "Last Names, First M; Last Names2, First2 M2"
    # so split by "; ", and then only take the last names bit of each name
    # by splitting by ","
    return "/".join([surg.split(",")[0] for surg in s.split("; ")])


def fix_ms_data(dat):
    """
    Takes a list of rows with multi-surgeon data and
    returns a list with one case per row.
    """
    # rows are ["OR...", "Surg2...", "Surg3...", "OR...", ...]
    # so join them together with "; ",
    # sub in a \n at each new case (representated by "OR" (or "MGW OR"))
    # then split the resultant string by the new \n to get one case per item
    return re.sub(r"; ((MGW )?OR \d+)", r"\n\1", "; ".join(dat)).split("\n")


def extract_cases(dat):
    """ Takes a TSV copy data and returns a rows of cases."""
    # ss = single surgeon; ms = multi-surgeon
    ss_dat = []
    ms_dat = []
    # useful to see if rows aren't full length due to mult surgeons
    ncols = 0
    for n, row in enumerate(dat):
        # add 1st row which is the headers
        if n == 0:
            ss_dat.append(row)
            # 1st row always has correct length for a ss case, so set ncols off it
            ncols = len(row.split("\t"))
        # skip blank rows
        elif not row.strip():
            continue
        # single surgeon rows always have correct number of items
        elif len(row.split("\t")) == ncols:
            ss_dat.append(row)
        # add not fitting rows to the "multi-surgeon" list
        # as when there are multi-surgeons, it copies and pastes them across
        # multiple lines
        else:
            ms_dat.append(row)
    return ss_dat + fix_ms_data(ms_dat)


def tidy(cases):
    """Takes list of TSV cases and returns tidied list of case dicts."""
    tidiers = {
        "Patient Class": tidy_patient_class,
        "Patient Name": tidy_patient_name,
        "Procedure": tidy_procedure,
        "Residents/Fellows": lambda x: "",
        "Room": tidy_room,
        "Surgeons": tidy_surgeons,
        "Time": str,
    }

    tidied_cases = []
    for row in csv.DictReader(cases, dialect="excel-tab"):
        # Add on cases have no "OR NN" so make it "Add On"
        if row["Progress Status"] == "Add On":
            row["Room"] = "Add On"
        tidied_case = {}
        for k, v in row.items():
            if k in tidiers:
                tidied_case[k] = tidiers[k](v)
        tidied_cases.append(tidied_case)

    return tidied_cases


def make_pastable_tsv(case_dicts):
    """Takes case_dicts and outputs a sorted TSV to copy to a spreadsheet."""
    columns = [
        "Room",
        "Time",
        "Patient Name",
        "Surgeons",
        "Procedure",
        "Patient Class",
        "Residents/Fellows",
    ]
    # add header
    tsv = ["\t".join(columns)]
    # add case rows
    for r in sorted(case_dicts, key=lambda r: r["Room"] + r["Time"]):
        tsv.append("\t".join(r[c] for c in columns))
    return "\r\n".join(tsv)


def main():
    """Take OR table clipboard contents, format nicely, & put into clipboard buffer."""
    # take pasted input, with new rows represented with linebreaks, split it,
    # and throw out first two rows as they are nonsense always
    # ss_dat, ms_dat = extract_data(pyperclip.paste().split("\r\n")[2:])
    cases = extract_cases(pyperclip.paste().splitlines()[2:])
    tidied_case_dicts = tidy(cases)
    pyperclip.copy(make_pastable_tsv(tidied_case_dicts))


if __name__ == "__main__":
    main()
