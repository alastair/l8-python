import struct
import serial
import bluetooth #pybluez!

HEADER_MSB = 0xAA
HEADER_LSB = 0x55
CMD_LED_SET = 0x43
CMD_MATRIX_SET = 0x44
CMD_MATRIX_OFF = 0x45


crcTable = [0, 7, 14, 9, 28, 27, 18, 21, 56, 63, 54, 49, 36, 35, 42, 45, 112,
119, 126, 121, 108, 107, 98, 101, 72, 79, 70, 65, 84, 83, 90, 93, 224, 231,
238, 233, 252, 251, 242, 245, 216, 223, 214, 209, 196, 195, 202, 205, 144, 151,
158, 153, 140, 139, 130, 133, 168, 175, 166, 161, 180, 179, 186, 189, 199, 192,
201, 206, 219, 220, 213, 210, 255, 248, 241, 246, 227, 228, 237, 234, 183, 176,
185, 190, 171, 172, 165, 162, 143, 136, 129, 134, 147, 148, 157, 154, 39, 32,
41, 46, 59, 60, 53, 50, 31, 24, 17, 22, 3, 4, 13, 10, 87, 80, 89, 94, 75, 76,
69, 66, 111, 104, 97, 102, 115, 116, 125, 122, 137, 142, 135, 128, 149, 146,
155, 156, 177, 182, 191, 184, 173, 170, 163, 164, 249, 254, 247, 240, 229, 226,
235, 236, 193, 198, 207, 200, 221, 218, 211, 212, 105, 110, 103, 96, 117, 114,
123, 124, 81, 86, 95, 88, 77, 74, 67, 68, 25, 30, 23, 16, 5, 2, 11, 12, 33, 38,
47, 40, 61, 58, 51, 52, 78, 73, 64, 71, 82, 85, 92, 91, 118, 113, 120, 127,
106, 109, 100, 99, 62, 57, 48, 55, 34, 37, 44, 43, 6, 1, 8, 15, 26, 29, 20, 19,
174, 169, 160, 167, 178, 181, 188, 187, 150, 145, 152, 159, 138, 141, 132, 131,
222, 217, 208, 215, 194, 197, 204, 203, 230, 225, 232, 239, 250, 253, 244, 243]

def docrc(block):
    crc = 0
    for i in block:
       b = struct.unpack("B", i)[0]
       crc = crcTable[crc ^ (b & 0xFF)];
    return crc;

class L8(object):
    """ The wire format for the L8 is straightforward:
    0xAA 0x55 len command data crc
    len, command, and crc are all 1 byte long. The length
    measures the size of the command and data fields.
    """

    def set_light(self, x, y, colour):
        """ cmd for set is 0x43
        x and y position in next 2 bytes
        followed by 3 bytes for colour:
        0xblue 0xgreen 0xred (0-f)
        (size needs to be 6)
        """
        cmd = struct.pack("BBBBBB", HEADER_MSB, HEADER_LSB, 6, CMD_LED_SET, x, y)
        cmd += struct.pack("BBB", colour.b, colour.g, colour.r)
        c = docrc(cmd[3:])
        cmd += struct.pack("B", c)
        self.write(cmd)

    def back_light(self, colour):
        """
        Super LED
        same as set with x=0x0a, y=0x0d
        """
        self.set_light(0x0a, 0x0d, colour)

    def send_matrix(self, colours):
        """
        cmd for matrix set: 0x44.
        Data should be 8x8. Note that the length is 128, not 64 because
        we need 2 bytes to store the colour for each of the 3 leds
        """
        numrows = len(colours)
        numcols = len(colours[0])

        cmd = struct.pack("BBBB", HEADER_MSB, HEADER_LSB, 1 + numrows*numcols*2, CMD_MATRIX_SET)

        for r in colours:
            for c in r:
                cmd += struct.pack("B",(c.b>>4)&0x0f)
                cmd += struct.pack("B", (c.g)&0xf0 | (c.r>>4)&0x0f)

        c = docrc(cmd[3:])
        cmd += struct.pack("B", c)
        self.write(cmd)

    def send_clear(self):
        """ Clear the screen. """
        cmd = struct.pack("BBBB", HEADER_MSB, HEADER_LSB, 1, CMD_MATRIX_OFF)
        c = docrc(cmd[3:])
        cmd += struct.pack("B", c)
        self.write(cmd)

    def send_text(self, speed, colour, text, repeat=False):
        """
        command: 0x83
        repeat, speed, r, g, b, text
        Note that colour is set as rgb, not bgr as in the other LED commands
        Text is ascii!
        """
        if repeat:
            r = 0x01
        else:
            r = 0x00
        size = 6 + len(text) # cmd rpt spd r g b txt
        cmd = struct.pack("BBBB", HEADER_MSB, HEADER_LSB, size, 0x83)
        cmd += struct.pack("B", r)
        cmd += struct.pack("B", speed)
        cmd += struct.pack("B", colour.r)
        cmd += struct.pack("B", colour.g)
        cmd += struct.pack("B", colour.b)
        cmd += struct.pack("B"*len(text), *[ord(t) for t in text])
        c = docrc(cmd[3:])
        cmd += struct.pack("B", c)
        self.write(cmd)

    def send_command(self, cmd, args):
        size = len(args) + 1 # cmd + args
        cmd = struct.pack("BBBB", HEADER_MSB, HEADER_LSB, size, cmd)
        for a in args:
            cmd += struct.pack("B", a)
        c = docrc(cmd[3:])
        cmd += struct.pack("B", c)
        self.write(cmd)


class L8Bt(L8):
    def __init__(self, address):
        self.BT_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        port = 1
        try:
            self.BT_socket.connect((address, port))
        except:
            print("ERROR: Could not connect")
            self.BT_socket.close()
            return -1
        
        self.BT_socket.settimeout(0.0) # Non blocking

    def write(self, data):
        self.BT_socket.send(data)

class L8Serial(L8):
    def __init__(self, device):
        self.socket = serial.Serial(device)

    def write(self, data):
        self.socket.write(data)


class Colour(object):
    r = 0
    g = 0
    b = 0

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def decay(self):
        rate = 0.6
        self.r = int(self.r * rate)
        self.g = int(self.g * rate)
        self.b = int(self.b * rate)

def get_initial_matrix():
    matrix = []
    for i in range(8):
        row = []
        for j in range(8):
            row.append(Colour(0, 0, 255))
        matrix.append(row)
    return matrix


