"""Writes launcher/icon.ico: a 4 x 4 slice of an ATT&CK-style matrix, one technique cell highlighted."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def make(out):
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, 248, 248), radius=44, fill="#14213D")
    for r in range(4):
        for c in range(4):
            x, y = 40 + c * 46, 40 + r * 46
            d.rounded_rectangle((x, y, x + 38, y + 38), radius=6, fill="#B7791F" if (r, c) == (1, 2) else "#1D4E89" if (r + c) % 3 else "#DCE3EC")
    im.save(out, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


if __name__ == "__main__":
    make(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "icon.ico")
