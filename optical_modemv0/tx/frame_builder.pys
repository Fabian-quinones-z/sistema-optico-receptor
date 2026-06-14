import numpy as np

from common.config import *


def build_frame(bits):

    if len(bits) < BITS_PER_FRAME:
        bits = bits.ljust(BITS_PER_FRAME, "0")

    bits = bits[:BITS_PER_FRAME]

    frame = np.zeros(
        (FRAME_SIZE, FRAME_SIZE),
        dtype=np.uint8
    )

    idx = 0

    for r in range(GRID_ROWS):

        for c in range(GRID_COLS):

            y1 = r * CELL_SIZE
            y2 = y1 + CELL_SIZE

            x1 = c * CELL_SIZE
            x2 = x1 + CELL_SIZE

            color = 255 if bits[idx] == "1" else 0

            frame[y1:y2, x1:x2] = color

            idx += 1

    return frame
