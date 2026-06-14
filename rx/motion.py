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

    diff = cv2.absdiff(gris, prev_frame)
    _, diff = cv2.threshold(diff, 128, 255, cv2.THRESH_BINARY)

    historial.append(diff)

    if len(historial) > VENTANA:
        historial.pop(0)

    acumulada = np.zeros_like(diff)

    for d in historial:
        acumulada = cv2.bitwise_or(acumulada, d)

    score = np.sum(acumulada > 0)

    prev_frame = gris.copy()

    return score, acumulada


def eliminar_lineas_cruz_avanzado(binaria):
    """
    Elimina líneas en cruz de la bandera SYNC
    """
    h, w = binaria.shape
    centro_x = w // 2
    centro_y = h // 2
    grosor = max(1, min(h, w) // 40)
    
    mascara_lineas = np.zeros_like(binaria)
    
    # Línea horizontal central
    y1 = max(0, centro_y - grosor)
    y2 = min(h, centro_y + grosor)
    mascara_lineas[y1:y2, :] = 255
    
    # Línea vertical central
    x1 = max(0, centro_x - grosor)
    x2 = min(w, centro_x + grosor)
    mascara_lineas[:, x1:x2] = 255
    
    resultado = cv2.bitwise_and(binaria, cv2.bitwise_not(mascara_lineas))
    
    return resultado


def encontrar_pantalla_mejorado(imagen):

    contours, _ = cv2.findContours(
        imagen,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    h, w = imagen.shape[:2]

    mejor = None
    mejor_area = 0

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area < h*w*0.08:
            continue

        rect = cv2.minAreaRect(cnt)

        ancho = rect[1][0]
        alto  = rect[1][1]

        if ancho < 30 or alto < 30:
            continue

        rect_area = ancho * alto

        if rect_area <= 0:
            continue

        solidity = area / rect_area

        if solidity < 0.45:
            continue

        if area > mejor_area:

            mejor_area = area

            mejor = np.int32(
                cv2.boxPoints(rect)
            )

    if mejor is None:
        return None

    return mejor.reshape((-1,1,2))
