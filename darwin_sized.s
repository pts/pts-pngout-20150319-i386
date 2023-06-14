#
# darwin_sized.s: creates a macOS 10.5 Mach-O executable with proper section sizes
# by pts@fazekas.hu at Fri May  5 19:36:30 CEST 2023
#
# Compile: i386-apple-darwin14-gcc -mmacosx-version-min=10.5 -W -Wall -O2 -march=i386 -fno-pic -fno-builtin -Wl,-read_only_relocs,suppress -Wl,-image_base,0x8048000 -s -o darwin_sized darwin_sized.s
#
# This file is of historical interest only, because pngoutd.nasm (TARGET==d
# for pngouta.nasm) was based on it. All the development is now done in
# pngouta.nasm. However, the Mach-O headers there are still not symbolic,
# i.e. it won't be possible to add an extern libc function there; for that,
# this file has to be modified, and then recompiled with
# i386-apple-darwin14-gcc (from https://github.com/pts/pts-osxcross).
#

.macosx_version_min 10, 5
.subsections_via_symbols

.section __TEXT,__text,regular,pure_instructions
_text_before_padding:

# !! These lines are for debugging, they can be removed.
	movl $_text, %eax
	movl $_text_end, %eax
	movl $_rodata, %eax
	movl $_rodata_end, %eax
	movl $_data, %eax
	movl $_data_end, %eax
	movl $_bss, %eax
	movl $_bss_end, %eax
#08048ce6        movl    $0x8048d10, %eax        ## imm = 0x8048D10
#08048ceb        movl    $0x805a698, %eax        ## imm = 0x805A698
#08048cf0        movl    $0x805a740, %eax        ## imm = 0x805A740
#08048cf5        movl    $0x805ba20, %eax        ## imm = 0x805BA20
#08048cfa        movl    $0x805d1c4, %eax        ## imm = 0x805D1C4
#08048cff        movl    $0x805d1f0, %eax        ## imm = 0x805D1F0
#08048d04        movl    $0x805d225, %eax        ## imm = 0x805D225
#08048d09        movl    $0x987ca40, %eax        ## imm = 0x987CA40

.fill 2, 1, 0x90
_text:  # Addr: 0x8048d10

#.align 4, 0x90
.globl _call_rest
_call_rest:                             ## @call_rest
	pushl %ebp
	movl %esp, %ebp
	subl $8, %esp
	calll _log           # calll   0x805bd7c
	calll _read          # calll   0x805bdac
	calll _printf        # calll   0x805bd9a
	calll _memmove       # calll   0x805bd8e
	calll _free          # calll   0x805bd5e
	calll _fgets         # calll   0x805bd46
	calll _fclose        # calll   0x805bd34
	calll _time          # calll   0x805bdfa
	calll _gettimeofday  # calll   0x805bd76
	calll _stpcpy        # calll   0x805bdbe
	calll _fseek         # calll   0x805bd64
	calll _fwrite        # calll   0x805bd70
	calll _strcat        # calll   0x805bdca
	calll _fread         # calll   0x805bd58
	calll _strcpy        # calll   0x805bdd6
	calll _realloc       # calll   0x805bdb2
	calll _malloc        # calll   0x805bd82
	calll _puts          # calll   0x805bda0
	calll _exit          # calll   0x805bd2e
	calll _srand         # calll   0x805bdb8
	calll _strchr        # calll   0x805bdd0
	calll _strcasecmp    # calll   0x805bdc4
	calll _ftell         # calll   0x805bd6a
	calll _fopen         # calll   0x805bd52
	calll _memset        # calll   0x805bd94
	calll _fileno        # calll   0x805bd4c
	calll _strtod        # calll   0x805bde8
	calll _fgetc         # calll   0x805bd40
	calll _strncasecmp   # calll   0x805bde2
	calll _rand          # calll   0x805bda6
	calll _strtok        # calll   0x805bdee
	addl $8, %esp        
	popl %ebp
	jmp _strtol                 ## TAILCALL
.globl _my_fprintf
#.align 4, 0x90
_my_fprintf:                            ## @my_fprintf
	pushl %ebp
	movl %esp, %ebp
	subl $24, %esp
	movl 8(%ebp), %eax
	movl 12(%ebp), %ecx
	leal 16(%ebp), %edx
	movl %edx, -4(%ebp)
	movl %edx, 8(%esp)
	movl %ecx, 4(%esp)
	movl %eax, (%esp)
	calll _vfprintf  # calll 0x805be00
	addl $24, %esp
	popl %ebp
	retl
.globl _main
#.align 4, 0x90
_main:                                  ## @main
	pushl %ebp
	movl %esp, %ebp
	subl $24, %esp
	movl $_name_in_rodata, (%esp)
	calll _strlen  # calll 0x805bddc
	incl %eax
	movl %eax, 8(%esp)
	movl $_name_in_rodata, 4(%esp)
	movl $_buf_in_bss, (%esp)
	calll _memcpy  # calll 0x805bd88
	movl ___stdoutp, %eax
	movl %eax, (%esp)
	movl $_buf_in_bss, 8(%esp)
	movl $_pattern_in_data, 4(%esp)
	calll _my_fprintf
	movl ___stdoutp, %eax
	movl %eax, (%esp)
	calll _fflush  # calll 0x805bd3a
	addl $24, %esp
	popl %ebp
	retl

	movl $_bss_end, %eax  # Debug.
.fill 0x11858+4-5-6, 1, 0x90
_name_in_rodata:                        ## @name_in_rodata
	.asciz "World"
# Addr: 0x805a697
	incl %eax
_text_end:
# Addr: 0x805a698

.fill 0xa8, 1, 0x90

#.section __TEXT, __const  # No explicit .rodata, there is too little room between .text and .rodata.
# Addr: 0x805a740
_rodata:
.long 3
_IO_stdin_used:
# Addr: 0x805a744
.long 0x201

# Addr: 0x805a748
message_on_sigint:
.ascii "Press ^C again to exit immediately."
.byte 10
.long 0
# Addr: 0x805a770
.fill 0x15bd-0x30d, 1, 0x90
_rodata_end:
# Addr: 0x805ba20

.fill 0x30d, 1, 0x90
# Addr: 0x805bd2d
_rodata_padding_end:

.section __DATA, __data
.fill 0x805d1c0-0x805c0ac, 1, 0x01
_data:  # Addr: 0x805d1c4
_pattern_in_data:                       ## @pattern_in_data
	.asciz "Hello, %s!\n"
.fill 0x805d1f0-0x805d1c4-12, 1, 0x02
_data_end:  # Addr: 0x805d1f0.

.zerofill __DATA,__bss,_bss_prefix,0x25,0 ## @buf_in_bss
.section __DATA, __bss
_bss:  # Addr: 0x805d225
.zerofill __DATA,__bss,_buf_in_bss,0x181f81b,0 ## @buf_in_bss
_bss_end:  # Addr: 0x987ca40

# __END__
