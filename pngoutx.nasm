;
; pngoutx.nasm: PNGOUT statically linked for Linux i386 using uClibc (106992 bytes)
; by pts@fazekas.hu at Fri May  5 15:57:26 CEST 2023
;
; Compile: tools/nasm-0.98.39 -O0 -w+orphan-labels -f bin -o pngoutx pngoutx.nasm && chmod +x pngoutx && cmp pngoutx.golden pngoutx && echo OK
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
;   uClibc. The entire file was remastered as a byproduct.
; * stdout output buffer (1024 bytes) is larger than in glibc 2.19 (1024
;   bytes for TTY, larger for non-TTY) for non-TTY. Also buffer boundaries
;   are different by a few bytes (sometimes uClibc flushes at 1023 bytes).
;
; Memory map and file layout with -Ttext=0x8042000:
;
;   .ELF_ehdr  0x00000..0x00034  +0x00034    ---
;   .ELF_phdr  0x00034..0x00094  +0x00060    ---
;   .gap1      0x00094..0x004c0  +0x0042c    ---
;   .ucrodata  0x004c0..0x01adc  +0x0161c    @0x80424c0...0x8043adc
;   .gap2      0x01adc..0x01ae0  +0x00004    @0x8043adc...0x8043ae0
;   .uctext    0x01ae0..0x06d09  +0x05229    @0x8043ae0...0x8048d09  ndisasm -b 32 -e 0x01ae0 -o 0x8043ae0 pngoutx >pngoutx.ndisasm
;   .gap3      0x06d09..0x06d10  +0x00007    @0x8048d09...0x8048d10
;   .text      0x06d10..0x18698  +0x11988    @0x8048d10...0x805a698
;   .gap5      0x18698..0x1876c  +0x000d4    @0x805a698...0x805a76c
;   .rodata    0x1876c..0x19a20  +0x012b4    @0x805a76c...0x805ba20
;   .gap6      0x19a20..0x19f40  +0x00520    @0x805ba20...0x805cf40  memsize=infilesize+0x1000=0x1520, virtual memory gap
;   .ucdata    0x19f40..0x1a1ac  +0x0026c    @0x805cf40...0x805d1ac
;   .gap7      0x1a1ac..0x1a1c4  +0x00018    @0x805d1ac...0x805d1c4
;   .data      0x1a1c4..0x1a1f0  +0x0002c    @0x805d1c4...0x805d1f0  file_size=end_off=0x1a1f0=106992 (previous is 122880 bytes)
;   .gap8      ---               +0x35       @0x805d1f0...0x805d225
;   .bss       ---               +0x181f82b  @0x805d225...0x987ca50
;   .ucbss     ---               +0x023e0    @0x987ca50...0x987ee20
;
;   LOAD       0x00000..0x19a20  +0x19a20    @0x8042000...0x805ba20  r-x
;   LOAD       0x19f40..0x1a1f0  +0x002b0    @0x805cf40...0x987ee20  rw-  memsize=+0x1821ee0
;   STACK      ---               ---         --                      rw-
;
;   .textgap4  0x09570..0x09660  +0x000f0    @0x804b570...0x804b660  filled with nop
;   .textgap5  0x096b0..0x0978e  +0x000de    @0x804b6b0...0x804b78e  filled with nop
;
; Commands generating the pngout_libc executable (with FAKE_main only) (may not work for copy-pasting now, it used to have the incorrect -Tbss=0x987ca50):
;
;   # ld.bin (GNU gold) doesn't fully respect -Ttext=0x8043ae0 (it puts it 4 bytes earlier)
;   # `qq ld' is Ubuntu 18.04 i386 GNU ld 2.24.
;   $ qq ld -nostdlib -m elf_i386 -static -o pngoutx_libc -z noexecstack -Ttext=0x8043ae0 --section-start .rodata=0x80424c0 -Tdata=0x805cf40 -Tbss=0x987ca50 xlib/start.o true.o xlib/libcu.o
;   $ objdump -x pngoutx_libc | head -40
;   $ objdump -x pngoutx_libc >pngoutx_libc.lst0
;
; Sections in file pngoutx_libc:
;
;   Name       File off  Size      Align  Addr
;   .uctext    0x01ae0   +0x05229  2**2   @0x8043ae0...0x8048d09
;   .ucrodata  0x004c0   +0x0161c  2**5   @0x80424c0...0x8043adc
;   .ucdata    0x06f40   +0x0026c  2**5   @0x805cf40...0x805d1ac
;   .ucbss     0x07a40   +0x023e0  2**5   @0x987ca40...0x987ee20
;
; Sections in file pngoutl:
;
;   .text+.rodata off=0x00000000 vaddr 0x8048000 align 2**12 filesz 0x13ad4 memsz 0x0013ad4 flags r-x
;   .data+.bss    off=0x00013f00 vaddr 0x805cf00 align 2**12 filesz 0x002f0 memsz 0x181fb28 flags rw-
;

%define TARGET x
%include "pngouta.nasm"

; __END__
