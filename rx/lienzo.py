import cv2
import numpy as np

from common.config import *

_referencia = None


def guardar_referencia(frame):

    global _referencia

    _referencia = frame.copy()


def obtener_referencia():

    return _referencia


def obtener_resta(frame):

    global _referencia

    if _referencia is None:
        return None

    return cv2.absdiff(
        frame,
        _referencia
    )


def encontrar_lienzo_por_resta(diff):

    if diff is None:
        return None

    _, th = cv2.threshold(
        diff,
        20,
        255,
        cv2.THRESH_BINARY
    )

    kernel = np.ones((7, 7), np.uint8)

    th = cv2.morphologyEx(
        th,
        cv2.MORPH_CLOSE,
        kernel
    )

    contours, _ = cv2.findContours(
        th,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    mejor = None
    mejor_area = 0

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area < LIENZO_MIN_AREA:
            continue

        if area > LIENZO_MAX_AREA:
            continue

        peri = cv2.arcLength(
            cnt,
            True
        )

        approx = cv2.approxPolyDP(
            cnt,
            0.02 * peri,
            True
        )

        if len(approx) != 4:
            continue

        if area > mejor_area:

            mejor_area = area
            mejor = approx

    return mejor
