import cv2
import numpy as np

prev_frame = None

historial = []

VENTANA = 5


def detectar_cambio(gris):

    global prev_frame
    global historial

    if prev_frame is None:

        prev_frame = gris.copy()

        return 0, None

    diff = cv2.absdiff(
        gris,
        prev_frame
    )

    _, diff = cv2.threshold(
        diff,
        40,
        255,
        cv2.THRESH_BINARY
    )

    historial.append(diff)

    if len(historial) > VENTANA:
        historial.pop(0)

    acumulada = np.zeros_like(diff)

    for d in historial:

        acumulada = cv2.bitwise_or(
            acumulada,
            d
        )

    score = np.sum(
        acumulada > 0
    )

    prev_frame = gris.copy()

    return score, acumulada




def encontrar_pantalla(edges):

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )

    for cnt in contours:

        peri = cv2.arcLength(
            cnt,
            True
        )

        approx = cv2.approxPolyDP(
            cnt,
            0.02 * peri,
            True
        )

        if len(approx) == 4:

            return approx

    return None
