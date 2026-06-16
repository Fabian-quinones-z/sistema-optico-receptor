import cv2
import numpy as np


def detectar_sync(
    estado0,
    estado1,
    area_min=8000):
    print("sincronizando ")
    """
    Detecta los recuadros generados por:

        Estado0 -> Estado1

    Devuelve:

    {
        "diff": diff,
        "mask": th,
        "recuadros": [...],
        "roi": (x,y,w,h)
    }
    """

    if estado0 is None:
        return None

    if estado1 is None:
        return None

    diff = cv2.absdiff(
        estado0,
        estado1
    )

    _, th = cv2.threshold(
        diff,
        20,
        255,
        cv2.THRESH_BINARY
    )

    kernel = np.ones((5,5), np.uint8)

    th = cv2.morphologyEx(
        th,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    contours, _ = cv2.findContours(
        th,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    recuadros = []

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area < area_min:
            continue

        x,y,w,h = cv2.boundingRect(cnt)

        recuadros.append({
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "cx": x + w//2,
            "cy": y + h//2,
            "area": area
        })

    recuadros.sort(
        key=lambda r: r["x"]
    )

    roi = None

    if len(recuadros) >= 2:

        izquierda = recuadros[0]
        derecha   = recuadros[-1]

        x1 = izquierda["x"] + izquierda["w"]
        x2 = derecha["x"]

        y1 = min(
            izquierda["y"],
            derecha["y"]
        )

        y2 = max(
            izquierda["y"] + izquierda["h"],
            derecha["y"] + derecha["h"]
        )

        roi = (
            x1,
            y1,
            max(1, x2 - x1),
            max(1, y2 - y1)
        )

    return {
        "diff": diff,
        "mask": th,
        "recuadros": recuadros,
        "roi": roi
    }
