import cv2
import numpy as np


def detectar_lineas(img):

    edges = cv2.Canny(
        img,
        50,
        150
    )

    return cv2.HoughLinesP(
        edges,
        1,
        np.pi/180,
        50,
        minLineLength=50,
        maxLineGap=10
    )


def angulo_dominante(lines):

    if lines is None:
        return 0

    angulos = []

    for l in lines:

        x1,y1,x2,y2 = l[0]

        angulo = np.degrees(
            np.arctan2(
                y2-y1,
                x2-x1
            )
        )

        if abs(angulo) < 45:
            angulos.append(angulo)

    if len(angulos) == 0:
        return 0

    return np.median(angulos)
