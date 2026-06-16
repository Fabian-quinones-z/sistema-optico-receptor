import cv2
import numpy as np

from common.config import *


def ordenar_esquinas(pts):

    pts = np.array(
        pts,
        dtype=np.float32
    )

    rect = np.zeros(
        (4, 2),
        dtype=np.float32
    )

    s = pts.sum(axis=1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)

    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def rectificar(frame, cuadrado):

    if cuadrado is None:
        return None

    pts = cuadrado.reshape(4, 2)

    rect = ordenar_esquinas(pts)

    dst = np.array(
        [
            [0, 0],
            [RECTIFIED_SIZE - 1, 0],
            [RECTIFIED_SIZE - 1, RECTIFIED_SIZE - 1],
            [0, RECTIFIED_SIZE - 1]
        ],
        dtype=np.float32
    )

    M = cv2.getPerspectiveTransform(
        rect,
        dst
    )

    return cv2.warpPerspective(
        frame,
        M,
        (RECTIFIED_SIZE, RECTIFIED_SIZE)
    )
