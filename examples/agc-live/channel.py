"""
channel.py -- talk to the AGC emulator over its socket.

The emulator (yaAGC) puts every I/O channel on a TCP socket, port 19697.
Each packet is 4 bytes. The DSKY, the IMU, the radar, and anything else
attached to the machine all use this one connection. This script is the
smallest possible piece of hardware: it logs what the AGC sends and it
presses DSKY keys.

    python channel.py --log out.bin --keys "V35E" --seconds 5

--log FILE     write every packet this script sends to FILE (4 bytes each);
               what the AGC sends back is counted, and the emulator's own
               AGC_TRACE_CHANNELS log has it in both directions
--keys TEXT    press these keys, in order, with a short pause between
--seconds N    stay connected this long (default 5)
--port N       emulator port (default 19697)

Key text: V N E (verb, noun, enter), digits, + - , C (clear), K (key
release), R (reset), P (proceed). Spaces are ignored. "V35E" is the
lamp test. "V16N36E" shows the mission clock. "V37E00E" is P00.

Packet form (from the emulator's own code, agc_utilities.c):
    byte 0:  channel >> 3
    byte 1:  0x40 | (channel & 7) << 3 | (value >> 12) & 7
    byte 2:  0x80 | (value >> 6) & 0x3f
    byte 3:  0xc0 | value & 0x3f
Keys go to channel 015 (octal). PRO is bit 14 of channel 032, with a
mask packet on channel 0432 first.
"""
import socket
import sys
import time

KEYS = {
    '0': 16, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, 'V': 17, 'N': 31, 'E': 28, 'C': 30, 'K': 25, 'R': 18,
    '+': 26, '-': 27,
}


def packet(channel, value):
    return bytes([
        channel >> 3,
        0x40 | ((channel << 3) & 0x38) | ((value >> 12) & 0x07),
        0x80 | ((value >> 6) & 0x3f),
        0xc0 | (value & 0x3f),
    ])


def unpacket(b):
    channel = (b[0] << 3) | ((b[1] >> 3) & 7)
    value = ((b[1] & 7) << 12) | ((b[2] & 0x3f) << 6) | (b[3] & 0x3f)
    return channel, value


def send(sock, log, data):
    sock.sendall(data)
    if log:
        log.write(data)


def press(sock, log, key):
    if key == 'P':                                  # PRO is a level, not a code
        send(sock, log, packet(0o432, 0o20000) + packet(0o32, 0))        # down
        time.sleep(0.2)
        send(sock, log, packet(0o432, 0o20000) + packet(0o32, 0o20000))  # up
    else:
        send(sock, log, packet(0o15, KEYS[key]))


def main(argv):
    opts = {'log': None, 'keys': '', 'seconds': '5', 'port': '19697'}
    i = 0
    while i < len(argv):
        if argv[i].startswith('--'):
            opts[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            i += 1
    sock = socket.create_connection(('127.0.0.1', int(opts['port'])))
    sock.settimeout(0.05)
    log = open(opts['log'], 'wb') if opts['log'] else None
    keys = [k for k in opts['keys'].upper() if k != ' ']
    end = time.time() + float(opts['seconds'])
    next_key = time.time() + 1.0        # let the machine settle first
    received = 0
    sent = 0
    while time.time() < end:
        try:
            data = sock.recv(4096)
            received += len(data) // 4
        except socket.timeout:
            pass
        if keys and time.time() >= next_key:
            press(sock, log, keys.pop(0))
            sent += 1
            next_key = time.time() + 0.4
    sock.close()
    if log:
        log.close()
    print(f'pressed {sent} keys, received {received} packets from the AGC')


if __name__ == '__main__':
    main(sys.argv[1:])
