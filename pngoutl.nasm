;
; pngoutl.nasm: PNGOUT dynamically linked for Linux i386 against glibc, remastered (82416 bytes)
; by pts@fazekas.hu at Fri May  5 15:57:26 CEST 2023
;
; Compile: tools/nasm-0.98.39 -O0 -w+orphan-labels -f bin -o pngoutl pngoutl.nasm && chmod +x pngoutl && cmp pngoutl.golden pngoutl && echo OK
;
; Based on pngoutss.nasm.
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
;
; Notes:
;
; * The `qq gcc' was a gcc run on Ubuntu 14.04 i386 system with gcc 4.8.4, ld
;   (binutils) 2.24, glibc 2.19.
; * -Wl,-z,norelro would make it 256 bytes smaller, but after recalculating
;   of the start address of .data, 256 bytes have to be added back, so
;   there is no size gain. Making the ELF section header shorter doesn't make
;   the file smaller either. However, we keep it, to make it compatible with
;   older Linux systems.
; * -Wl,--hash-style=sysv wouldn't make the executable larger.
;

%define TARGET l
%include "pngoutx.nasm"

; __END__
