#! /usr/bin/python
# by pts@fazekas.hu at Mon May  8 02:16:57 CEST 2023
#
# This is a Python 2 script, it works e.g. with Python 2.7.
#

import binascii
import subprocess
import sys
import struct

class Part(object):
  __slots__ = ('name', 'ptype', 'addr', 'off', 'size')

  def __init__(self, name, ptype, addr, off, size):
    self.name, self.ptype, self.addr, self.off, self.size = (
        name, ptype, addr, off, size)


def main(argv):
  parts = (
      Part('P.ELF_ehdr',          '??',          0x8048000,  0x00000,    0x000034),
      Part('P.ELF_phdr',          '??',          0x8048034,  0x00034,    0x000100),
      Part('P.interp',            'PROGBITS',    0x8048134,  0x0000134,  0x0000013 + 1),
      Part('P.note.ABI_tag',      'NOTE',        0x8048148,  0x0000148,  0x0000020),
      Part('P.gnu.hash',          'GNU_HASH',    0x8048168,  0x0000168,  0x0000030),
      Part('P.dynsym',            'DYNSYM',      0x8048198,  0x0000198,  0x00002e0),
      Part('P.dynstr',            'STRTAB',      0x8048478,  0x0000478,  0x000019f + 1),
      Part('P.gnu.version',       'VERSYM',      0x8048618,  0x0000618,  0x000005c),
      Part('P.gnu.version_r',     'VERNEED',     0x8048674,  0x0000674,  0x0000050),
      Part('P.rel.dyn',           'REL',         0x80486c4,  0x00006c4,  0x0000020),
      Part('P.rel.plt',           'REL',         0x80486e4,  0x00006e4,  0x0000130),
      Part('P.init',              'CODEBITS',    0x8048814,  0x0000814,  0x0000023 + 9),
      Part('P.plt',               'CODEBITS',    0x8048840,  0x0000840,  0x0000270 + 0x100),
      Part('P.text',              'CODEBITS',    0x8048bb0,  0x0000bb0,  0x0011b62 + 2),
      Part('P.fini',              'CODEBITS',    0x805a714,  0x0012714,  0x0000014),
      Part('P.rodata',            'PROGBITS',    0x805a728,  0x0012728,  0x00012f8),
      Part('P.eh_frame_hdr',      'PROGBITS',    0x805ba20,  0x0013a20,  0x0000024),
      Part('P.eh_frame',          'PROGBITS',    0x805ba44,  0x0013a44,  0x0000090 + 0x52c),
      Part('P.init_array',        'INIT_ARRAY',  0x805d000,  0x0014000,  0x0000004),
      Part('P.fini_array',        'FINI_ARRAY',  0x805d004,  0x0014004,  0x0000004),
      Part('P.jcr',               'PROGBITS',    0x805d008,  0x0014008,  0x0000004),
      Part('P.dynamic',           'DYNAMIC',     0x805d00c,  0x001400c,  0x00000f0),
      Part('P.got',               'PROGBITS',    0x805d0fc,  0x00140fc,  0x0000004),
      Part('P.got.plt',           'PROGBITS',    0x805d100,  0x0014100,  0x00000a4),
      Part('P.data',              'PROGBITS',    0x805d1a4,  0x00141a4,  0x000024c),
      Part('P.bss',               'NOBITS',      0x805d400,  0x00143f0,  0x181f840),
  )
  labels = (
  )

  target_labels_dict = {
  }

  labels_dict = dict(labels)
  pending_labels = set(labels_dict)
  if len(labels) != len(labels_dict):
    raise ValueError('Duplicate label name.')
  labels_dict_rev = {}
  for name, addr in labels:
    if addr not in labels_dict_rev:
      labels_dict_rev[addr] = []
    labels_dict_rev[addr].append(name)
  final_end_ofs = 0x143f0
  f = open('pngoutl.golden', 'rb')
  fo = open('pngoutl2.nasm', 'wb')

  addr = 0x8042000
  fo.write('; Generated by %s\n'  % argv[0])
  fo.write('; Compile: tools/nasm-0.98.39 -O0 -w+orphan-labels -f bin -o pngoutl pngoutl.nasm\n')
  fo.write('bits 32\ncpu 386\norg 0\nR.code equ $-0x%x\n' % addr)
  ofs = 0
  for part in parts:
    if ofs != part.off:
      raise ValueError('ofs mismatch: name=%s ofs=0x%x part.off=0x%x' % (part.name, ofs, part.off))
    if addr > part.addr:
      raise ValueError('addr too large: part=%s addr=0x%x part.addr=0x%x' % (part.name, addr, part.addr))
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
            if addr in labels_dict_rev:
              for name in labels_dict_rev[addr]:
                fo.write(';%s:\n' % name)
                pending_labels.remove(name)
            line_addr, line_hex, line_instr = line.split(None, 2)
            # print [line_addr, line_hex, line_instr]
            line_addr = int(line_addr, 16)
            if line_addr != addr:
              raise ValueError('ndisasm addr mismatch: addr=0x%x line_addr=0x%x' % (addr, line_addr))
            data = binascii.unhexlify(line_hex)
            #if len(data) == 1:  # Single-byte i386 instructions have an unambiguous decoding.
            #  fo.write('..@0x%x: %s\n' % (addr, line_instr))
            #elif data.startswith('\xff\x35') and len(data) == 6:
            #  fo.write('..@0x%x: push dword [0x%x]\n' % (addr, struct.unpack('<L', data[2:])[0]))
            #elif data.startswith('\x68') and len(data) == 5:
            #  fo.write('..@0x%x: push 0x%x\n' % (addr, struct.unpack('<L', data[1:])[0]))
            #elif data.startswith('\xff\x25') and len(data) == 6:
            #  fo.write('..@0x%x: jmp [0x%x]\n' % (addr, struct.unpack('<L', data[2:])[0]))
            special = ''
            if data.startswith('\xe8') and len(data) == 5:  # call 0x....
              target_addr = int(line_instr.split(None, 1)[1], 16)
              if target_addr in labels_dict_rev:
                name = labels_dict_rev[target_addr][0]
                if name in target_labels_dict:
                  target_addr = target_labels_dict[name]
                  special = '..@0x%x: call R.code+0x%x  ; Patched %s.\n' % (addr, target_addr, name)
            elif data.startswith('\xa1') and len(data) == 5:  # mov eax, [0x...]
              target_addr = int(line_instr.split(',', 1)[1].strip('[]'), 16)
              if target_addr in labels_dict_rev:
                name = labels_dict_rev[target_addr][0]
                if name in target_labels_dict:
                  target_addr = target_labels_dict[name]
                  special = '..@0x%x: mov eax, [0x%x]  ; Patched %s.\n' % (addr, target_addr, name)
            #elif data.startswith('\xe9') and len(data) == 5:  # jmp 0x....
            #  target_addr = int(line_instr.split(None, 1)[1], 16)
            #  fo.write('..@0x%x: jmp strict near R.code+0x%x\n' % (addr, target_addr))
            if special:
              fo.write(special)
            else:
              fo.write('..@0x%x: db %s  ;; %s\n' % (addr, ', '.join('0x%02x' % ord(b) for b in data), line_instr))
          addr += len(data)
          ofs += len(data)
        # addr, ofs = end_addr, end_ofs
      else:
        while addr != end_addr:
          line_size = min(16 - (addr & 15), end_addr - addr)
          assert line_size
          data = f.read(line_size)
          if len(data) != line_size:
            raise ValueError('Input file too short: part=%s' % (part.name,))
          fo.write('..@0x%x: db %s\n' % (addr, ', '.join('0x%02x' % ord(b) for b in data)))
          addr += line_size
          ofs += line_size
    else:
      fo.write('absolute $\n')
      addr = part.addr
      fo.write('..@0x%x: resb 0x%x\n' % (addr, part.size))
  if ofs != final_end_ofs:
    raise ValueError('final_end_ofs mismatch: ofs=0x%x final_end_ofs=0x%x' % (ofs, final_end_ofs))
  #if pending_labels:
  #  raise ValueError('Pending (not-yet-defined) labels: %s' % ', '.join(sorted(pending_labels)))
  fo.write('\n; __END__\n')


if __name__ == '__main__':
  sys.exit(main(sys.argv))
