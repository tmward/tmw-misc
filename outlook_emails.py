#!/usr/bin/env python3

"""
Takes the clipboard contents from the copied names and emails from an outlook
recipients list and returns, in the clipboard copy buffer, a two-column
tab-separated text of
"name\temail"
"name2\temail2"
...
etc.
which you can copy into a spreadsheet.
"""

import re
import pyperclip


def main():
    emails_raw = pyperclip.paste()
    name_email_regex = re.compile(r"\"(.+?)\" <(.+?)>")
    name_emails = [f"{n}\t{e}" for n, e in sorted(name_email_regex.findall(emails_raw))]
    pyperclip.copy("\n".join(name_emails))


if __name__ == "__main__":
    main()
