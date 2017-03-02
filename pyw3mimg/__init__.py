#!/usr/bin/env python3

import enum
import subprocess


class W3MOpcode(enum.IntEnum):
    """
    Represents the opcodes for w3mimgdisplay.
    """
    #: Draw image opcode.
    DRAW = 0

    #: Redraw image opcode.
    REDRAW = 1

    #: Terminate drawing.
    TERMINATE = 2

    #: Sync drawing.
    SYNC_DRAWING = 3

    #: Sync communication.
    SYNC_COMMUNICATION = 4

    #: Get size of image.
    GET_SIZE = 5

    #: Clear image.
    CLEAR_IMAGE = 6


class W3MImageDisplay(object):
    """
    Wraps ``w3mimgdisplay`` to display images in the terminal.
    """

    def __init__(self, path: str = 'w3mimgdisplay', auto_sync=True):
        """
        :param path: The **full** path to ``w3mimgdisplay``. 
            For Linux systems, this is usually ``/usr/lib/w3m/w3mimgdisplay``.
        
        :param auto_sync: Should the communication be automatically synched?
        """
        self._path = path
        self._auto_sync = auto_sync
        self._proc = subprocess.Popen(self._path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def __del__(self):
        self.terminate()
        self._proc.communicate()

    def write(self, data: bytes):
        """
        Write to the underlying W3M subprocess.
        
        :param data: The data to write. 
        """
        self._proc.stdin.write(data)
        self._proc.stdin.flush()

    def _draw(self, op: W3MOpcode, path: str, n, x, y, w=0, h=0, sx=0, sy=0, sw=0, sh=0):
        """
        Internal draw command.
        """
        self.write(b'%d;%d;%d;%d;%d;%d;%d;%d;%d;%d;%s\n' % (op, n, x, y, w, h, sx, sy, sw, sh, path.encode()))
        if self._auto_sync:
            self.sync()

    def draw(self, path: str, n: int, x: int, y: int,
             w: int = 0, h: int = 0, sx: int = 0, sy: int = 0, sw: int = 0, sh: int =0):
        """
        Draws an image to the screen.
        
        :param path: The image path to draw.
        :param n: The index of the image to draw. Used for multiple images.
        :param x: The X position for the top left corner.
        :param y: The Y position for the top left corner.
        :param w: The width of the drawn image. Defaults to sw.
        :param h: The height of the image. Defaults to sh.
        :param sx: The X offset of the image (presumably where to take data from inside the image file).
        :param sy: The Y offset of the image.
        :param sw: The "source width" of the image.
        :param sh: The "source height" of the image.
        """
        self._draw(W3MOpcode.DRAW, path, n, x, y, w, h, sx, sy, sw, sh)

    def redraw(self, path, n, x, y, w=0, h=0, sx=0, sy=0, sw=0, sh=0):
        """
        Re-draws the image on the terminal (?).
        
        :param path: The image path to draw.
        :param n: The index of the image to redraw. 
        :param x: The X position for the top left corner.
        :param y: The Y position for the top left corner.
        :param w: The width of the drawn image. Defaults to sw.
        :param h: The height of the image. Defaults to sh.
        :param sx: The X offset of the image (presumably where to take data from inside the image file).
        :param sy: The Y offset of the image.
        :param sw: The "source width" of the image.
        :param sh: The "source height" of the image.
        """
        self._draw(W3MOpcode.REDRAW, path, n, x, y, w, h, sx, sy, sw, sh)

    def terminate(self):
        """
        Terminates drawing.
        """
        self.write(b'2;\n')

    def sync(self):
        """
        Syncs drawing.
        """
        self.write(b'3;\n')

    def nop(self):
        """
        Syncs communication (?).
        """
        self.write(b'4;\n')
        self._proc.stdout.readline()

    def get_size(self, path: str):
        """
        Gets the size of an image.
        
        :param path: The path to the image.
        """
        self.write(b'5;%s\n' % path)
        wh = self._proc.stdout.readline().decode().split(" ")
        return int(wh[0]), int(wh[1])

    def clear(self, x, y, w, h):
        """
        Clears (?) drawing.
        """
        self.write(b'6;%d;%d;%d;%d\n' % (x, y, w, h))

if __name__ == "__main__":
    d = W3MImageDisplay(path="/usr/lib/w3m/w3mimgdisplay")
    filename = input("Enter filename to display: ")
    d.draw(filename, n=1, x=0, y=0)
