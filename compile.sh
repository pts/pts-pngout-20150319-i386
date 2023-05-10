#! /bin/sh --
#
# compile.sh: compile i386 PNGOUT sources with NASM, build executables
# by pts@fazekas.hu at Tue May  9 00:33:29 CEST 2023
#

NASM="${NASM:-tools/nasm-0.98.39}"  # Works on Linux i386 and Linux amd64.
NASMOPT="${NASMOPT:--O0}"
set -ex

for F in pngoutl.nasm pngoutlo.nasm pngoutls.nasm pngoutx.nasm pngoutd.nasm; do
  BF="${F%.*}"
  # It should produce identical output with -O999999999 as with -O0.
  "$NASM" "$NASMOPT" -w+orphan-labels -f bin -o "$BF" "$F"
  chmod +x "$BF"
  cmp "$BF".golden "$BF"
done

: "$0" OK.
