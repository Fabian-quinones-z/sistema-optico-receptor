import cv2

from common.config import *

def demodulate_image(path):

    img = cv2.imread(path, 0)

    bits = ""

    for r in range(GRID_ROWS):

        for c in range(GRID_COLS):

            y = r * CELL_SIZE + CELL_SIZE // 2
            x = c * CELL_SIZE + CELL_SIZE // 2

            pixel = img[y, x]

            bits += '1' if pixel > THRESHOLD else '0'

    return bits
