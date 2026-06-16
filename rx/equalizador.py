import cv2

from common.config import *
import numpy as np


def equalizar(gris):

    kernel = np.array(
        [
            [1,0,1],
            [0,1,1],
            [0,1,0]
        ],
        dtype=np.uint8
    )

    gris = cv2.bilateralFilter(
        gris,
        8,
        170,
        180
    )

    gris = cv2.medianBlur(
        gris,
        INDICE_BLUR
    )

    clahe = cv2.createCLAHE(
        clipLimit=4.3,
        tileGridSize=(4,4)
    )

    gris = clahe.apply(gris)

    gris = cv2.morphologyEx(
        gris,
        cv2.MORPH_CLOSE,
        kernel
    )

    gris = cv2.normalize(
        gris,
        None,
        30,
        124,
        cv2.NORM_MINMAX
    )

    return gris


def binarizar(gris):

    if USE_OTSU:

        _, binaria = cv2.threshold(
            gris,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

    else:

        _, binaria = cv2.threshold(
            gris,
            THRESHOLD_BINARIO,
            255,
            cv2.THRESH_BINARY
        )

    return binaria
