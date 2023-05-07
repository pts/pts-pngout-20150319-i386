#! /usr/bin/python
# by pts@fazekas.hu at Thu May  4 20:52:34 CEST 2023
#
# This is a Python 2 script, it works e.g. with Python 2.7.
#

import binascii
import re
import struct
import subprocess
import sys


class Part(object):
  __slots__ = ('name', 'ptype', 'addr', 'off', 'size')

  def __init__(self, name, ptype, addr, off, size):
    self.name, self.ptype, self.addr, self.off, self.size = (
        name, ptype, addr, off, size)

def main(argv):
  parts = (
      Part('P.ELF_phdr',          '??',          0x8048000, 0x00000, 0x000034),
      Part('P.ELF_ehdr',          '??',          0x8048034, 0x00034, 0x000100),
      Part('P.interp',            'PROGBITS',    0x8048134, 0x00134, 0x000013 + 1),
      Part('P.note.ABI_tag',      'NOTE',        0x8048148, 0x00148, 0x000020),
      Part('P.note.gnu.build_id', 'NOTE',        0x8048168, 0x00168, 0x000024),
      Part('P.hash',              'HASH',        0x804818c, 0x0018c, 0x000164),
      Part('P.gnu.hash',          'GNU_HASH',    0x80482f0, 0x002f0, 0x000030),
      Part('P.dynsym',            'DYNSYM',      0x8048320, 0x00320, 0x000320),
      Part('P.dynstr',            'STRTAB',      0x8048640, 0x00640, 0x0001a1 + 1),
      Part('P.gnu.version',       'VERSYM',      0x80487e2, 0x007e2, 0x000064 + 2),
      Part('P.gnu.version_r',     'VERNEED',     0x8048848, 0x00848, 0x000050),
      Part('P.rel.dyn',           'REL',         0x8048898, 0x00898, 0x000020),
      Part('P.rel.plt',           'REL',         0x80488b8, 0x008b8, 0x000160),
      Part('P.init',              'CODEBITS',    0x8048a18, 0x00a18, 0x000026 + 2),
      Part('P.plt',               'CODEBITS',    0x8048a40, 0x00a40, 0x0002d0),
      Part('P.text',              'CODEBITS',    0x8048d10, 0x00d10, 0x011a00),
      Part('P.fini',              'CODEBITS',    0x805a710, 0x12710, 0x000017 + 0x19),
      Part('P.rodata',            'PROGBITS',    0x805a740, 0x12740, 0x0012e0),
      Part('P.eh_frame_hdr',      'PROGBITS',    0x805ba20, 0x13a20, 0x00020c),
      Part('P.eh_frame',          'PROGBITS',    0x805bc2c, 0x13c2c, 0x000d04 + 0x6d0),
      Part('P.init_array',        'INIT_ARRAY',  0x805d000, 0x15000, 0x000004),
      Part('P.fini_array',        'FINI_ARRAY',  0x805d004, 0x15004, 0x000004),
      Part('P.jcr',               'PROGBITS',    0x805d008, 0x15008, 0x000004),
      Part('P.dynamic',           'DYNAMIC',     0x805d00c, 0x1500c, 0x0000f8),
      Part('P.got',               'PROGBITS',    0x805d104, 0x15104, 0x000004),
      Part('P.got.plt',           'PROGBITS',    0x805d108, 0x15108, 0x0000bc),
      Part('P.data',              'PROGBITS',    0x805d1c4, 0x151c4, 0x00002c),
      Part('P.ELF_sections',      'PROGBITS',    0xa000000, 0x151f0, 0x0005b8),
      #Part('P.bss',               'NOBITS',      0x805d1f0, 0x151f0, 0x181f850),  # Will be edited manually.
  )
  labels = (
      ('log@plt', 0x8048a50),
      ('read@plt', 0x8048a60),
      ('printf@plt', 0x8048a70),
      ('fflush@plt', 0x8048a80),
      ('memmove@plt', 0x8048a90),
      ('free@plt', 0x8048aa0),
      ('memcpy@plt', 0x8048ab0),
      ('fgets@plt', 0x8048ac0),
      ('fclose@plt', 0x8048ad0),
      ('time@plt', 0x8048ae0),
      ('gettimeofday@plt', 0x8048af0),
      ('stpcpy@plt', 0x8048b00),
      ('fseek@plt', 0x8048b10),
      ('fwrite@plt', 0x8048b20),
      ('strcat@plt', 0x8048b30),
      ('fread@plt', 0x8048b40),
      ('strcpy@plt', 0x8048b50),
      ('realloc@plt', 0x8048b60),
      ('malloc@plt', 0x8048b70),
      ('puts@plt', 0x8048b80),
      ('__fxstat@plt', 0x8048b90),
      ('__gmon_start__@plt', 0x8048ba0),
      ('exit@plt', 0x8048bb0),
      ('srand@plt', 0x8048bc0),
      ('strchr@plt', 0x8048bd0),
      ('strlen@plt', 0x8048be0),
      ('__libc_start_main@plt', 0x8048bf0),
      ('strcasecmp@plt', 0x8048c00),
      ('ftell@plt', 0x8048c10),
      ('fopen@plt', 0x8048c20),
      ('memset@plt', 0x8048c30),
      ('fileno@plt', 0x8048c40),
      ('strtod@plt', 0x8048c50),
      ('fgetc@plt', 0x8048c60),
      ('strncasecmp@plt', 0x8048c70),
      ('rand@plt', 0x8048c80),
      ('strtok@plt', 0x8048c90),
      ('sigemptyset@plt', 0x8048ca0),
      ('vfprintf@plt', 0x8048cb0),
      ('readdir@plt', 0x8048cc0),
      ('sigaction@plt', 0x8048cd0),
      ('strtol@plt', 0x8048ce0),
      ('closedir@plt', 0x8048cf0),
      ('opendir@plt', 0x8048d00),

      ('log@addr', 0x805d114),
      ('read@addr', 0x805d118),
      ('printf@addr', 0x805d11c),
      ('fflush@addr', 0x805d120),
      ('memmove@addr', 0x805d124),
      ('free@addr', 0x805d128),
      ('memcpy@addr', 0x805d12c),
      ('fgets@addr', 0x805d130),
      ('fclose@addr', 0x805d134),
      ('time@addr', 0x805d138),
      ('gettimeofday@addr', 0x805d13c),
      ('stpcpy@addr', 0x805d140),
      ('fseek@addr', 0x805d144),
      ('fwrite@addr', 0x805d148),
      ('strcat@addr', 0x805d14c),
      ('fread@addr', 0x805d150),
      ('strcpy@addr', 0x805d154),
      ('realloc@addr', 0x805d158),
      ('malloc@addr', 0x805d15c),
      ('puts@addr', 0x805d160),
      ('__fxstat@addr', 0x805d164),
      ('__gmon_start__@addr', 0x805d168),
      ('exit@addr', 0x805d16c),
      ('srand@addr', 0x805d170),
      ('strchr@addr', 0x805d174),
      ('strlen@addr', 0x805d178),
      ('__libc_start_main@addr', 0x805d17c),
      ('strcasecmp@addr', 0x805d180),
      ('ftell@addr', 0x805d184),
      ('fopen@addr', 0x805d188),
      ('memset@addr', 0x805d18c),
      ('fileno@addr', 0x805d190),
      ('strtod@addr', 0x805d194),
      ('fgetc@addr', 0x805d198),
      ('strncasecmp@addr', 0x805d19c),
      ('rand@addr', 0x805d1a0),
      ('strtok@addr', 0x805d1a4),
      ('sigemptyset@addr', 0x805d1a8),
      ('vfprintf@addr', 0x805d1ac),
      ('readdir@addr', 0x805d1b0),
      ('sigaction@addr', 0x805d1b4),
      ('strtol@addr', 0x805d1b8),
      ('closedir@addr', 0x805d1bc),
      ('opendir@addr', 0x805d1c0),

      ('_start', 0x804b570),
      ('_fini', 0x805a6a0),
      ('_init', 0x805a6b0),
      ('main', 0x80499c0),
      ('_init_func', 0x8048a18),
      ('_init_maybe_call_gmon_start', 0x8048a18),
      ('_fini_func', 0x805a710),
      ('_fini_dummy', 0x805a710),
      ('_plt0', 0x8048a40),
      ('_init_array_entry0', 0x804b630),
      ('_fini_array_entry0', 0x804b610),
      ('_init_array', 0x805d000),
      ('_fini_array', 0x805d004),
      ('_init_array_end', 0x805d004),
      ('_jcr_entry0@addr', 0x805d008),
      ('_fini_array_end', 0x805d008),
      ('_dynamic_init_array@daddr', 0x805d030),
      ('_dynamic_fini_array@daddr', 0x805d040),
      ('_dynamic_init_func@addr', 0x805d020),
      ('_dynamic_fini_func@addr', 0x805d028),
      ('_init_array_entry0@addr', 0x805d000),
      ('_fini_array_entry0@addr', 0x805d004),
      ('_fini_array_once', 0x804b5a0),
      ('_fini_array_once_flag', 0x805d224),
      ('_init_array_loop', 0x804b5d0),
      ('_init_fini_array_func@daddr', 0x805d1f0),

      ('_IO_stdin_used', 0x805a744),  # 1 or 2 bytes.

      ('stdin@daddr', 0x805d204),  # Contains a pointer to the `stdin' value, thus has type FILE**.
      ('stdout@daddr', 0x805d220),
      ('stderr@daddr', 0x805d200),

      ('global_struct_sigaction', 0x987c580),  # 140 bytes.
      ('global_cleanup_counter', 0x805d240),  # 4 bytes.
      ('str_message_on_sigint', 0x805a748),  # 0x24 bytes. ASCIIZ string.
      ('str_message_on_sigint.end', 0x805a748 + 0x24),  # 0x24 bytes.
      ('str_message_help_line1', 0x805a770),  # ASCIIZ string.
      ('str_message_help_line_last', 0x805ade4),
      ('str_release_date', 0x805b02f),  # ASCIIZ string.
      ('message_filep', 0x805d244),  # FILE *, 4 bytes, typically stderr, stdout or NULL.

      ('handle_sigint', 0x804b6b0),  # Code.
      ('setup_sigint_handler', 0x804b720),  # Code.
      ('unknown_func1', 0x80527b0),  # Code.
      ('unknown_func2', 0x8048d10),  # Code.
      ('unknown_func3', 0x8049677),  # Code.
      ('unknown_func4', 0x804b660),  # Code.
      ('message_printf', 0x804b680),  # Code.
      ('print_help', 0x804b790),  # Code.
      ('jmp_print_help_and_exit', 0x804b2ff),  # Code.
      ('jmp_exit1_after_printing_help', 0x804b304),  # Code.

      ('code_ptr_e_entry', 0x8048018),
      ('code_ptr_0x805b1dc', 0x805b1dc),
      ('code_ptr_0x805b1e0', 0x805b1e0),
      ('code_ptr_0x805b1e4', 0x805b1e4),
      ('code_ptr_0x805b1e8', 0x805b1e8),
      ('code_ptr_0x805b1ec', 0x805b1ec),
      ('code_ptr_0x805b1f0', 0x805b1f0),
      ('code_ptr_0x805b1f4', 0x805b1f4),
      ('code_ptr_0x805b1f8', 0x805b1f8),
      ('code_ptr_0x805b1fc', 0x805b1fc),
      ('code_ptr_0x805b200', 0x805b200),
      ('code_ptr_0x805b204', 0x805b204),
      ('code_ptr_0x805b208', 0x805b208),
      ('code_ptr_0x805b20c', 0x805b20c),
      ('code_ptr_0x805b210', 0x805b210),
      ('code_ptr_0x805b214', 0x805b214),
      ('code_ptr_0x805b218', 0x805b218),
      ('code_ptr_0x805b21c', 0x805b21c),
      ('code_ptr_0x805b220', 0x805b220),
      ('code_ptr_0x805b224', 0x805b224),
      ('code_ptr_0x805b228', 0x805b228),
      ('code_ptr_0x805b22c', 0x805b22c),
      ('code_ptr_0x805b230', 0x805b230),
      ('code_ptr_0x805b234', 0x805b234),
      ('code_ptr_0x805b238', 0x805b238),
      ('code_ptr_0x805b5e0', 0x805b5e0),
      ('code_ptr_0x805b5e4', 0x805b5e4),
      ('code_ptr_0x805b5e8', 0x805b5e8),
      ('code_ptr_0x805b5ec', 0x805b5ec),
      ('code_ptr_0x805b5f0', 0x805b5f0),
      ('code_ptr_0x805b5f4', 0x805b5f4),
      ('code_ptr_0x805b5f8', 0x805b5f8),
      ('code_ptr_0x805b5fc', 0x805b5fc),
      ('code_ptr_0x805b600', 0x805b600),
      ('code_ptr_0x805b604', 0x805b604),
      ('code_ptr_0x805b608', 0x805b608),
      ('code_ptr_0x805b60c', 0x805b60c),
      ('code_ptr_0x805b610', 0x805b610),
      ('code_ptr_0x805b614', 0x805b614),
      ('code_ptr_0x805b618', 0x805b618),
      ('code_ptr_0x805b61c', 0x805b61c),
      ('code_ptr_0x805b620', 0x805b620),
      ('code_ptr_0x805b624', 0x805b624),
      ('code_ptr_0x805b628', 0x805b628),
      ('code_ptr_0x805b62c', 0x805b62c),
      ('code_ptr_0x805b630', 0x805b630),
      ('code_ptr_0x805b634', 0x805b634),
      ('code_ptr_0x805b638', 0x805b638),
      ('code_ptr_0x805b63c', 0x805b63c),
      ('code_ptr_0x805b640', 0x805b640),
      ('code_ptr_0x805b644', 0x805b644),
      ('code_ptr_0x805b648', 0x805b648),
      ('code_ptr_0x805b64c', 0x805b64c),
      ('code_ptr_0x805b650', 0x805b650),
      ('code_ptr_0x805b654', 0x805b654),
      ('code_ptr_0x805b658', 0x805b658),
      ('code_ptr_0x805b65c', 0x805b65c),
      ('code_ptr_0x805b660', 0x805b660),
      ('code_ptr_0x805b664', 0x805b664),
      ('code_ptr_0x805b668', 0x805b668),
      ('code_ptr_0x805b66c', 0x805b66c),
      ('code_ptr_0x805b670', 0x805b670),
      ('code_ptr_0x805b674', 0x805b674),
      ('code_ptr_0x805b678', 0x805b678),
      ('code_ptr_0x805b67c', 0x805b67c),
      ('code_ptr_0x805b680', 0x805b680),
      ('code_ptr_0x805b684', 0x805b684),
      ('code_ptr_0x805b688', 0x805b688),
      ('code_ptr_0x805b68c', 0x805b68c),
      ('code_ptr_0x805b690', 0x805b690),
      ('code_ptr_0x805b694', 0x805b694),
      ('code_ptr_0x805b698', 0x805b698),
      ('code_ptr_0x805b69c', 0x805b69c),
      ('code_ptr_0x805b6a0', 0x805b6a0),
      ('code_ptr_0x805b6a4', 0x805b6a4),
      ('code_ptr_0x805b6a8', 0x805b6a8),
      ('code_ptr_0x805b6ac', 0x805b6ac),
      ('code_ptr_0x805b6b0', 0x805b6b0),
      ('code_ptr_0x805b6b4', 0x805b6b4),
      ('code_ptr_0x805b6b8', 0x805b6b8),
      ('code_ptr_0x805b6bc', 0x805b6bc),
      ('code_ptr_0x805b760', 0x805b760),
      ('code_ptr_0x805b764', 0x805b764),
      ('code_ptr_0x805b768', 0x805b768),
      ('code_ptr_0x805b76c', 0x805b76c),
      ('code_ptr_0x805b770', 0x805b770),
      ('code_ptr_0x805b774', 0x805b774),
      ('code_ptr_0x805b778', 0x805b778),
      ('code_ptr_0x805b77c', 0x805b77c),
      ('code_ptr_0x805b780', 0x805b780),
      ('code_ptr_0x805b784', 0x805b784),
      ('code_ptr_0x805b788', 0x805b788),
      ('code_ptr_0x805b78c', 0x805b78c),
      ('code_ptr_0x805b790', 0x805b790),
      ('code_ptr_0x805b794', 0x805b794),
      ('code_ptr_0x805b798', 0x805b798),
      ('code_ptr_0x805b79c', 0x805b79c),
      ('code_ptr_0x805b7a0', 0x805b7a0),
      ('code_ptr_0x805b7a4', 0x805b7a4),
      ('code_ptr_0x805b7a8', 0x805b7a8),
      ('code_ptr_0x805b7ac', 0x805b7ac),
      ('code_ptr_0x805b7b0', 0x805b7b0),
      ('code_ptr_0x805b7b4', 0x805b7b4),
      ('code_ptr_0x805b7b8', 0x805b7b8),
      ('code_ptr_0x805b7bc', 0x805b7bc),
      ('code_ptr_0x805b7c0', 0x805b7c0),
      ('code_ptr_0x805b7c4', 0x805b7c4),
      ('code_ptr_0x805b7c8', 0x805b7c8),
      ('code_ptr_0x805b7cc', 0x805b7cc),
      ('code_ptr_0x805b7d0', 0x805b7d0),
      ('code_ptr_0x805b7d4', 0x805b7d4),
      ('code_ptr_0x805b7d8', 0x805b7d8),
      ('code_ptr_0x805b7dc', 0x805b7dc),
      ('code_ptr_0x805b7e0', 0x805b7e0),
      ('code_ptr_0x805b7e4', 0x805b7e4),
      ('code_ptr_0x805b7e8', 0x805b7e8),
      ('code_ptr_0x805b7ec', 0x805b7ec),
      ('code_ptr_0x805b7f0', 0x805b7f0),
      ('code_ptr_0x805b7f4', 0x805b7f4),
      ('code_ptr_0x805b7f8', 0x805b7f8),
      ('code_ptr_0x805b7fc', 0x805b7fc),
      ('code_ptr_0x805b800', 0x805b800),
      ('code_ptr_0x805b804', 0x805b804),
      ('code_ptr_0x805b808', 0x805b808),
      ('code_ptr_0x805b80c', 0x805b80c),
      ('code_ptr_0x805b810', 0x805b810),
      ('code_ptr_0x805b814', 0x805b814),
      ('code_ptr_0x805b818', 0x805b818),
      ('code_ptr_0x805b81c', 0x805b81c),
      ('code_ptr_0x805b820', 0x805b820),
      ('code_ptr_0x805b824', 0x805b824),
      ('code_ptr_0x805b828', 0x805b828),
      ('code_ptr_0x805b82c', 0x805b82c),
      ('code_ptr_0x805b830', 0x805b830),
      ('code_ptr_0x805b834', 0x805b834),
      ('code_ptr_0x805b838', 0x805b838),
      ('code_ptr_0x805b83c', 0x805b83c),
      ('code_ptr_0x805b840', 0x805b840),
      ('code_ptr_0x805b844', 0x805b844),
      ('code_ptr_0x805b848', 0x805b848),
      ('code_ptr_0x805b84c', 0x805b84c),
      ('code_ptr_0x805b850', 0x805b850),
      ('code_ptr_0x805b854', 0x805b854),
      ('code_ptr_0x805b858', 0x805b858),
      ('code_ptr_0x805b85c', 0x805b85c),
      ('code_ptr_0x805b860', 0x805b860),
      ('code_ptr_0x805b864', 0x805b864),
      ('code_ptr_0x805b868', 0x805b868),
      ('code_ptr_0x805b86c', 0x805b86c),
      ('code_ptr_0x805b870', 0x805b870),
      ('code_ptr_0x805b874', 0x805b874),
      ('code_ptr_0x805b878', 0x805b878),
      ('code_ptr_0x805b87c', 0x805b87c),
      ('code_ptr_0x805b880', 0x805b880),
      ('code_ptr_0x805b884', 0x805b884),
      ('code_ptr_0x805b888', 0x805b888),
      ('code_ptr_0x805b88c', 0x805b88c),
      ('code_ptr_0x805d1cc', 0x805d1cc),
  )

  labels_dict = dict(labels)
  pending_labels = set(labels_dict)
  if len(labels) != len(labels_dict):
    raise ValueError('Duplicate label name.')
  labels_dict_rev = {}
  for name, addr in labels:
    if addr not in labels_dict_rev:
      labels_dict_rev[addr] = []
    labels_dict_rev[addr].append(name)
  end_ofs = 0x151f0
  code_start_addr = 0x8048a18
  code_end_addr = 0x805a710 + 0x17

  #hex_re = re.compile(r'0x([0-9a-f]+)')
  rcode_hex_re = re.compile(r'(?:R[.]code[+])?0x([0-9a-f]+)')
  def label_replacement(match):
    addr = int(match.group(1), 16)
    if addr in labels_dict_rev:
      addr = labels_dict_rev[addr][0]
      if match.group(0).startswith('R'):
        addr = 'B.code+' + addr
      return addr
    elif code_start_addr <= addr < code_end_addr:
      if match.group(0).startswith('R'):
        return match.group(0)
      else:
        return 'A.code+' + match.group(0)  # Just decoration.
    else:
      return match.group(0)
  def add_labels(instr):
    return rcode_hex_re.sub(label_replacement, instr)
  def write_labels(fo, addr, diff, name_suffix=''):
    is_dd = False
    if addr in labels_dict_rev:
      for name in labels_dict_rev[addr]:
        if name.endswith(name_suffix):
          if name in pending_labels:
            fo.write('%s: equ $+0x%x\n' % (name, diff))
            pending_labels.remove(name)
          if name.startswith('code_ptr_') or name.endswith('@addr') or name.endswith('@daddr'):
            is_dd = True
    return is_dd

  f = open('pngout.golden', 'rb')
  fo = open('pngout.nasm', 'wb')

  addr = 0x8048000
  fo.write('; Generated by %s\n'  % argv[0])
  fo.write('; Compile: tools/nasm-0.98.39 -O0 -w+orphan-labels -f bin -o pngout pngout.nasm && chmod +x pngout && cmp pngout.golden pngout && echo OK\n')
  fo.write('bits 32\ncpu 386\norg 0\nR.code equ $-0x%x\nB.code equ -0x%x\nA.code equ 0\n' % (addr, addr))
  ofs = 0
  for part in parts:
    if ofs != part.off:
      raise ValueError('ofs mismatch: ofs=0x%x part.off=0x%x' % (ofs, part.off))
    if addr > part.addr:
      raise ValueError('addr too large: addr=0x%x part.addr=0x%x' % (addr, part.addr))
    fo.write('\n%s:  ; addr=0x%x off=0x%x\n' % (part.name, part.addr, part.off))
    if part.name != 'P.bss':
      f.seek(ofs)
      end_ofs = part.off + part.size
      addr = part.addr
      end_addr = part.addr + part.size
      if part.ptype == 'CODEBITS':  # Disassemble with ndisasm(1).
        data = f.read(part.size)
        if len(data) != part.size:
          raise ValueError('Input file too short.')
        p = subprocess.Popen(('tools/ndisasm-0.98.39', '-b', '32', '-o', '0x%x' % addr, '-'), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
          data, _ = p.communicate(data)
        finally:
          exit_code = p.wait()
        if exit_code:
          raise RuntimeError('ndisasm failed.')
        for line in data.split('\n'):
          if not line:
            continue
          if line.startswith('         -'):  # Hex continuation of the previous instruction.
            line_hex = line[line.find('-') + 1:]
            data = binascii.unhexlify(line_hex)
            fo.write('..@0x%x: db %s\n' % (addr, ', '.join('0x%02x' % ord(b) for b in data)))
          else:
            write_labels(fo, addr, addr - ofs)
            line_addr, line_hex, line_instr = line.split(None, 2)
            # print [line_addr, line_hex, line_instr]
            line_addr = int(line_addr, 16)
            if line_addr != addr:
              raise ValueError('ndisasm addr mismatch: addr=0x%x line_addr=0x%x' % (addr, line_addr))
            data = binascii.unhexlify(line_hex)
            if len(data) == 1:  # Single-byte i386 instructions have an unambiguous decoding.
              fo.write('..@0x%x: %s\n' % (addr, add_labels(line_instr)))
            elif data.startswith('\xff\x35') and len(data) == 6:
              fo.write('..@0x%x: %s\n' % (addr, add_labels('push dword [0x%x]' % struct.unpack('<L', data[2:])[0])))
            elif data.startswith('\x68') and len(data) == 5:
              fo.write('..@0x%x: %s\n' % (addr, add_labels('push 0x%x' % struct.unpack('<L', data[1:])[0])))
            elif data.startswith('\xff\x25') and len(data) == 6:
              fo.write('..@0x%x: %s\n' % (addr, add_labels('jmp [0x%x]' % struct.unpack('<L', data[2:])[0])))
            elif data.startswith('\xe8') and len(data) == 5:  # call 0x....
              target_addr = int(line_instr.split(None, 1)[1], 16)
              fo.write('..@0x%x: %s\n' % (addr, add_labels('call R.code+0x%x' % target_addr)))
            elif data.startswith('\xe9') and len(data) == 5:  # jmp 0x....
              target_addr = int(line_instr.split(None, 1)[1], 16)
              fo.write('..@0x%x: %s\n' % (addr, add_labels('jmp strict near R.code+0x%x' % target_addr)))
            else:
              fo.write('..@0x%x: db %s  ;; %s\n' % (addr, ', '.join('0x%02x' % ord(b) for b in data), add_labels(line_instr)))
          addr += len(data)
          ofs += len(data)
        # addr, ofs = end_addr, end_ofs
        write_labels(fo, addr, addr - ofs, '_end')
      else:
        while addr != end_addr:
          line_size = min(16 - (addr & 15), end_addr - addr)
          for i in xrange(1, line_size):
            if addr + i in labels_dict_rev:
              line_size = i
              break
          assert line_size
          data = f.read(line_size)
          if len(data) != line_size:
            raise ValueError('Input file too short.')
          is_dd = write_labels(fo, addr, addr - ofs)
          line_end_addr = addr + line_size
          while addr < line_end_addr:
            #for i in xrange(line_end_addr - addr - 3):  # TODO(pts): Find unaligned pointers as well.
            #  addr2, = struct.unpack('<L', data[i : i + 4])
            #  if code_start_addr <= addr2 < code_end_addr:
            #    sys.stderr.write('      (\'code_ptr_0x%x\', 0x%x),\n' % (addr + i, addr + i))
            if is_dd and line_size >= 4:
              line_size = 4
              fo.write('..@0x%x: dd %s\n' % (addr, add_labels('0x%x' % struct.unpack('<L', data[:4])[0])))
              f.seek(ofs + 4)
              line_end_addr = addr + 4
            else:
              fo.write('..@0x%x: db %s\n' % (addr, ', '.join('0x%02x' % ord(b) for b in data)))
            addr += line_size
            ofs += line_size
        write_labels(fo, addr, addr - ofs, '_end')
    else:  # P.bss, must be the last.
      fo.write('absolute $\n')
      addr = part.addr
      end_addr = addr + part.size
      bss_label_addrs = sorted(laddr for laddr in (labels_dict[name] for name in pending_labels) if addr <= laddr <= end_addr)[::-1]
      addr_ofs_diff = addr - ofs
      while addr != end_addr:
        if bss_label_addrs and bss_label_addrs[-1] <= end_addr:
          resb_size = bss_label_addrs[-1] - addr
          if resb_size:
            fo.write('..@0x%x: resb 0x%x\n' % (addr, resb_size))
            addr += resb_size
          write_labels(fo, addr, addr_ofs_diff)
          bss_label_addrs.pop()
        else:
          fo.write('..@0x%x: resb 0x%x\n' % (addr, end_addr - addr))
          addr = end_addr
  if ofs != end_ofs:
    raise ValueError('end_ofs mismatch: ofs=0x%x end_ofs=0x%x' % (ofs, end_ofs))
  if pending_labels:
    #  !! TODO(pts): ValueError: Pending (not-yet-defined) labels: _fini_array_once_flag, _init_fini_array_func@daddr, global_cleanup_counter, global_struct_sigaction, message_filep, stderr@daddr, stdin@daddr, stdout@daddr
    if 0: raise ValueError('Pending (not-yet-defined) labels: %s' % ', '.join(sorted(pending_labels)))
  fo.write('\n; __END__\n')


if __name__ == '__main__':
  sys.exit(main(sys.argv))
