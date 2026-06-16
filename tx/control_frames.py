gitgimport numpy as np
from common.config import FRAME_SIZE

def sync_a():

    frame = np.zeros(
        (FRAME_SIZE, FRAME_SIZE),
        dtype=np.uint8
    )

    h = FRAME_SIZE // 2

    frame[0:h, 0:h] = 255
    frame[h:, h:] = 255

    return frame


def sync_b():

    frame = np.zeros(
        (FRAME_SIZE, FRAME_SIZE),
        dtype=np.uint8
    )

    h = FRAME_SIZE // 2

    frame[0:h, h:] = 255
    frame[h:, 0:h] = 255

    return frame
