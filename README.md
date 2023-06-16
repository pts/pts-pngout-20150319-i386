# pts-pngout-20150319-i386: Linux i386, macOS i386 and FreeBSD i386 ports of PNGOUT 20150319

pts-pngout-20150319-i386 is a collection of port of the PNG recompressor
tool PNGOUT, version 20150319 to various operating systems (Linux, macOS and
FreeBSD), targeting the i386 architecture, i686 == P6 processor family or
newer (first implemented by the Pentium Pro processor, launched on
1995-11-01). This port doesn't contain additional functionality, it just
makes PNGOUT work on more systems.

PNGOUT.EXE, the Windows version of PNGOUT (including version 20150319) is
written by Ken Silverman. It's not open source, but it's free to use and
there are some other freedoms with some conditions (see its
[license](http://advsys.net/ken/utils.htm#pngoutkziplicense)).

Jonathon Fowler has released some Linux, FreeBSD macOS ports of PNGOUT
(download [here](http://www.jonof.id.au/kenutils.html)), they are under the
same license as PNGOUT.EXE.

All ports in pts-pngout-20150319-i386 were based on the file
`pngout-20150319-linux/i686/pngout` (87976 bytes) within
[pngout-20150319-linux.tar.gz](https://www.jonof.id.au/files/kenutils/pngout-20150319-linux.tar.gz).
This ELF-32 executable program file is dynamically linked against Linux
glibc, and it was compiled with GCC 4.4.7 and 4.7.2 (one of them has likely
compiled the glibc stubs, the other one the program itself).

pts-pngout-20150319-i386 provides the following new ports:

* `pngoutd` (91880 bytes): macOS i386 port (as a Mach-O i386 executable)
  targeting macOS: Mac OS X 10.5 Leopard (released on 2007-10-26) ... 10.14
  Catalina (released on 2019-10-07). Newer versions of macOS aren't able to
  run it directly, because they don't support Mach-O i386 executables (i.e.
  ``32-bit apps''). It links dynamically against
  `/usr/lib/libSystem.B.dylib`. Some rarely used functionality (including
  directory listings) has been removed.

* `pngoutxf` (80460 bytes): FreeBSD i386 port, statically linked ELF-32
  executable program. It works on FreeBSD 3.0 (released on 1998-10-16) or
  newer. It also works on Linux i386 (and amd64) systems with the Linux
  kernel 2.4.0 (released on 2001-01-04) or later. That's not a coincidence,
  it detects the operating system at startup, and then it calls the matching
  syscalls. Some rarely used functionality (including directory listings)
  has been removed.

Who would benefit from these ports?

* Everyday Linux users would benefit from `pngoutxf`, because it's
  statically linked, thus it's independent of the system libc, thus it runs
  on more Linux distributions. Please note that Jonathon Fowler's Linux
  static ports also provide these benefits, at the expense of the executable
  files being at least 9.5 times larger than `pngoutxf`.

* Linux container users optimizing for container image size would benefit
  from `pngoutxf`, because it's smaller than any other ports, and it doesn't
  even need a libc. Similarly, FreeBSD jail users optimizing for code size
  would benefit.

* Users of very old Macs (which can only run 32-bit apps, i.e. any Apple
  hardware launched before 2006-09-06) would benefit from `pngoutd`. Newer
  Macs support 64-bit apps, and Jonathon Fowler's ports work.

* Users of very old macOS (Mac OS X 10.5 Leopard .. Mac OS X 10.7 Lion)
  would benefit from `pngoutd`. Jonathon Fowler's latest ports need Mac OS X
  10.8 Mountain Lion (released on 2012-07-25), and his older, 20150920 ports
  need Mac OS X 10.6 Snow Leopard (released on 2009-08-28).

pts-pngout-20150319-i386 provides the following ports as well, for
completeness and educational interest:

* `pngoutlo` (87976 bytes): Linux i386 port, ELF-32 executable program
  dynamically linked against glibc (`libc.so.6`). This file is bit-by-bit
  identical to the `pngout-20150319-linux/i686/pngout` file. It needs glibc
  2.1 (released on 1999-02-03) or later.

* `pngoutls` (86512 bytes): Linux i386 port, ELF-32 executable program
  dynamically linked against glibc (`libc.so.6`), stripped. ELF section
  headers and ELF symbols have been removed (i.e. stripped), to make the file
  a bit smaller. Otherwise it's the same as `pngoutlo`. It needs glibc
  2.1 (released on 1999-02-03) or later.

* `pngoutl` (82416 bytes): Linux i386 port, ELF-32 executable program
  dynamically linked against glibc (`libc.so.6`), stripped. Some rarely used
  functionality (including directory listings), ELF sections headers, ELF
  symbols and unnecessary ELF PT_DYNAMIC header entries have been removed,
  also some to make the file a bit smaller. It needs glibc
  2.1 (released on 1999-02-03) or later.

* `pngoutx` (80460 bytes): Linux i386 port, statically linked ELF-32
  executable program. It's like `pngoutxf`, but it doesn't contain the
  FreeBSD i386 syscall adapters, so it doesn't work on FreeBSD out of the
  box, but it works on FreeBSD if Linux emulation is enabled. Some rarely
  used functionality (including directory listings) has been removed. It
  needs the Linux kernel 2.4.0 (released on 2001-01-04) or later.

The pts-pngout-20150319-i386 repository conatains precompiled executables
for the ports above, having the `.golden` extension, e.g.
[pngoutxf.golden](https://github.com/pts/pts-pngout-20150319-i386/blob/master/pngoutxf.golden).
After downloading the file, rename it, and you are ready to run it. For
example:

  mv pngoutxf.golden pngoutxf
  chmod +x pngoutxf.golden
  ./pngoutxf

To build the executables above from NASM source code, compile the .nasm
source files with NASM. An example command:

  nasm -O0 -f bin -o pngoutxf pngoutxf.nasm
  chmod +x pngoutxf

For Linux i386, a bundled NASM 0.98.39 and a convenience shell script
`./compile.sh` is provided. The shell script will compile all ports with the
bundled NASM, and it will also check that the output matches the
corresponding `.golden` file.

The executables in pts-pngout-20150319-i386 are much smaller than those
released by Jonathon Fowler. That's because pts-pngout-20150319-i386 removes
all the unnecessary ELF headers and symbols, and it contains a minimalistic
custom libc optimized for size (rather than being statically linked against
bloated libcs such as glibc).

A quick size comparison with PNGOUT.EXE 2015:

* PNGOUT.EXE (for Windows i386, compressed, 20150213): 38912 bytes
* pngoutx (for Linux i386, uncompressed): 80460 bytes
* pngoutx.upxbc (for Linux i396, compressed with [upxbc](https://github.com/pts/upxbc)): 42299 bytes

  Compression command: `upxbc --elftiny --ultra-brute --no-lzma -f -o pngoutx.upxbc pngoutx`

Other ports of PNGOUT:

* [PNGOUT.EXE](http://advsys.net/ken/util/pngout.exe) (version 20150213,
  38912 bytes): Original PNGOUT for Win32, written by Ken Silverman.
* [Linux i386, amd64, armv7, aarch64, statically
  linked](http://www.jonof.id.au/files/kenutils/pngout-20200115-linux-static.tar.gz)
  port (version 20200115), created by Jonathon Fowler (JonoF).
* [Linux i386, amd64, armv7, aarch64, dynamically linked against
  glibc](http://www.jonof.id.au/files/kenutils/pngout-20200115-linux.tar.gz)
  port (version 20200115), created by Jonathon Fowler (JonoF).
* [FreeBSD i386, amd64, statically
  linked](http://www.jonof.id.au/files/kenutils/pngout-20200115-bsd-static.tar.gz)
  (version 20200115), created by Jonathon Fowler (JonoF).
* [FreeBSD i386, amd64, dynamically linked against FreeBSD
  libc](http://www.jonof.id.au/files/kenutils/pngout-20200115-bsd.tar.gz)
  (version 20200115), created by Jonathon Fowler (JonoF).
* [macOS amd64, aarch64, dynamically linked against macOS
  libSystem](http://www.jonof.id.au/files/kenutils/pngout-20230322-mac.zip)
  (version 20230322), created by Jonathon Fowler (JonoF).
