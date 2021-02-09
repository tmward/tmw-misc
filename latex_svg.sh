#!/bin/sh

# first argument: latex formula (no surrounding $ needed)
# second arg: filename for svg [default: formula.svg]
# requires: latex, dvisvgm

# build temporary files and enter environment
tmpdir=$(mktemp -d)
latexfile=$(mktemp -p "$tmpdir")
cd "$tmpdir" || exit

# make latex file and dvi
cat <<EOF >> "$latexfile" && latex "$latexfile" > /dev/null 2>&1 || exit
\documentclass{standalone}
\begin{document}
$ $1$
\end{document}
EOF

# make svg
svgfile="formula.svg"
if [ -n "$2" ]; then
    svgfile="$2"
fi
dvisvgm --no-fonts tmp -o "$OLDPWD/$svgfile" > /dev/null 2>&1
cd "$OLDPWD" || exit

# clean up
rm -Rf "$tmpdir"
