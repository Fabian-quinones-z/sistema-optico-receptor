"""
receiver.py

PIPELINE

FRAME
 │
 ▼
ROI
 │
 ▼
GRIS
 │
 ▼
BINARIA
 │
 ├── detectar_sync()
 │
 ├── detectar_lineas()
 │
 ├── angulo_dominante()
 │
 ├── rectify_frame()
 │
 └── detectar_cambio()
         │
         ▼
      BANDERA

FUTURO:
demodular_frame()
"""

import cv2

from rx.config_rx import *

from rx.sync import detectar_sync

from rx.geometry import (
    detectar_lineas,
    angulo_dominante
)

from rx.rectify import rectify_frame

from rx.motion import ( detectar_cambio , encontrar_pantalla)


# ==================================================
# INICIO VIDEO
# ==================================================

cap = cv2.VideoCapture(
    VIDEO_FILE
)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # ==================================================
    # ROI
    # ==================================================

    roi = frame[
        ROI_Y1:ROI_Y2,
        ROI_X1:ROI_X2
    ]

    roi = cv2.resize(
        roi,
        ROI_SIZE
    )

    if MOSTRAR_FRAME:

        debug_frame = frame.copy()

        cv2.rectangle(
            debug_frame,
            (ROI_X1, ROI_Y1),
            (ROI_X2, ROI_Y2),
            (0,255,0),
            2
        )

        cv2.imshow(
            "FRAME",
            debug_frame
        )

    # ==================================================
    # GRIS
    # ==================================================

    gris = cv2.cvtColor(
        roi,
        cv2.COLOR_BGR2GRAY
    )

    # ==================================================
    # CONFIGURAR THRESHOLD BINARIO
    # ==================================================

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

    if MOSTRAR_BINARIA:

        cv2.imshow(
            "BINARIA",
            binaria
        )

    # ==================================================
    # DETECTAR CAMBIO / BANDERAS
    # ==================================================

    score, diff = detectar_cambio(
        binaria
    )

    bandera = (
        score > CAMBIO_MINIMO
    )

    if MOSTRAR_DIFF:

        if diff is not None:

            cv2.imshow(
                "DIFF",
                diff
            )

    # ==================================================
    # DETECCION SYNC
    # ==================================================

    patron = detectar_sync(
        gris
    )

    # ==================================================
    # SI NO HAY SYNC
    # ==================================================

    if patron != "SYNC":

        tecla = cv2.waitKey(30)

        if tecla == 27:
            break

        continue

    # ==================================================
    # DETECTAR LINEAS
    # ==================================================

    lines = detectar_lineas(
        binaria
    )

    if lines is None:

        tecla = cv2.waitKey(30)

        if tecla == 27:
            break

        continue

    # ==================================================
    # DEBUG LINEAS
    # ==================================================

    if MOSTRAR_LINEAS:

        debug_lineas = roi.copy()

        for l in lines:

            x1, y1, x2, y2 = l[0]

            cv2.line(
                debug_lineas,
                (x1, y1),
                (x2, y2),
                (0,0,255),
                2
            )

        cv2.imshow(
            "LINEAS",
            debug_lineas
        )

    # ==================================================
    # ANGULO DOMINANTE
    # ==================================================

    ang = angulo_dominante(
        lines
    )

    # ==================================================
    # RECTIFICACION
    # ==================================================

    corregida = rectify_frame(
        roi,
        -ang
    )

    h, w = corregida.shape[:2]

    cx = w // 2
    cy = h // 2

    # ==================================================
    # CENTRO DE LECTURA DEL MENSAJE
    # ==================================================

    cv2.line(
        corregida,
        (cx,0),
        (cx,h),
        (0,255,0),
        1
    )

    cv2.line(
        corregida,
        (0,cy),
        (w,cy),
        (0,255,0),
        1
    )

    cv2.circle(
        corregida,
        (cx,cy),
        4,
        (0,0,255),
        -1
    )

    # ==================================================
    # VENTANA DE MUESTREO
    # ==================================================

    radio = 10

    lectura = corregida[
        max(0, cy-radio):min(h, cy+radio),
        max(0, cx-radio):min(w, cx+radio)
    ]

    intensidad = 0

    if lectura.size > 0:

        gris_lectura = cv2.cvtColor(
            lectura,
            cv2.COLOR_BGR2GRAY
        )

        intensidad = int(
            gris_lectura.mean()
        )

    # ==================================================
    # ESTADO DEL RECEPTOR
    # ==================================================

    estado = (
        f"SYNC "
        f"ANG={ang:.1f} "
        f"FLAG={int(bandera)} "
        f"SCORE={score} "
        f"PIX={intensidad}"
    )

    cv2.putText(
        corregida,
        estado,
        (10,20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0,255,0),
        1
    )

    # ==================================================
    # FUTURA DEMODULACION
    # ==================================================
    #
    # if bandera:
    #
    #     bits = demodular_frame(
    #         corregida
    #     )
    #
    #     mensaje = decodificar(
    #         bits
    #     )
    #
    # ==================================================

    if MOSTRAR_RECTIFICADA:

        cv2.imshow(
            "RECTIFICADA",
            corregida
        )

    tecla = cv2.waitKey(30)

    if tecla == 27:
        break

# ==================================================
# FIN
# ==================================================

cap.release()

cv2.destroyAllWindows()
