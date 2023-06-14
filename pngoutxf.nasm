;
; pngoutx.nasm: PNGOUT statically linked for FreeBSD i386 and Linux i386 using a custom libc (80460 bytes)
; by pts@fazekas.hu at Wed Jun 14 13:09:07 CEST 2023
;
; Compile: tools/nasm-0.98.39 -O0 -w+orphan-labels -f bin -o pngoutxf pngoutxf.nasm && chmod +x pngoutxf && cmp pngoutxf.golden pngoutxf && echo OK
;
; Based on: pngout-20150319-linux/i686/pngout in https://www.jonof.id.au/files/kenutils/pngout-20150319-linux.tar.gz (87976 bytes)
; Based on: https://www.jonof.id.au/files/kenutils/
;
; Status and TODOs:
;
; * It works on Linux i386 and Linux amd64.
;
; Differences from pngout above:
;
; * The double-SIGINT-to-exit feature was removed, and the default on Linux
;   is to exit on the first SIGINT.
; * Calls to opendir(2), readdir(2) and closedir(2) were replaced with a
;   stub which always returns an error.
; * Calls to __fxstat(2) were replaced with a stub which always returns an
;   error.
; * glibc crt*.o init and fini routines were removed.
; * The remaining code was remastered in `nasm -f elf' source format. 5560
;   bytes were saved in the executable as a byproduct of this remastering.
; * gcc + ld was dropped as a dependency, the output execuable is generated
;   by nasm only, thus it is more deterministic.
; * ELF section headers ware stripped from the end of the file (not needed
;   for execution).
; * EI_OSABI in ELF_phdr were changed from SYSV to Linux.
; * Dynamic linking against glibc was replaced with static linking against
;   uClibc 0.9.30.1 (released on 2009-03-02). The entire file was remastered
;   as a byproduct.
; * stdout output buffer (1024 bytes) is larger than in glibc 2.19 (1024
;   bytes for TTY, larger for non-TTY) for non-TTY. Also buffer boundaries
;   are different by a few bytes (sometimes uClibc flushes at 1023 bytes).
; * uClibc functions were gradually replaced with functions from a
;   size-optimized custom libc tailored for this pts-pngout port, and
;   finally all uClibc functions and variables have been replaced. (The
;   custom libc is available separately as well
;   (https://github.com/pts/minilibc686 , e.g.
;   https://github.com/pts/minilibc686/blob/master/src/strtod.nasm)
; * By using a custom libc, it was possible to reduce the executable program
;   size from 106992 bytes (uClibc) to 80460 bytes (custom libc), even
;   smaller than the original after stripping (pngoutls, 86512 bytes),
;   even smaller than the hand-optimized version dynamically linked against
;   glibc (pngoutl, 82416 bytes).
; * FreeBSD i386 compatibility was added to to pngoutx.nasm while retaning
;   Linux i386 compatibility with operating system autodetection.
;   pngoutx.nasm remains Linux-only. See freebsd_port.md for a documentation
;   of the porting process.
; * See pngoutx.nasm for the memory and file layout.
;

%define TARGET xf
%include "pngouta.nasm"

; __END__
