import cv2
import numpy as np

from rx.config_rx import *
from rx.sync import detectar_sync
from rx.motion import detectar_cambio
from rx.geometry import erosionar_bits

from rx.cuadrado import ordenar_esquinas

from rx.signal import es_pulso_valido 
from rx.demodulation import demodular_frame

cap = cv2.VideoCapture(0)  #VIDEO_FILE)   #0) # cambiamos entre video archivo y camara*(0)


def equalizar(gris):
    """Versión optimizada para comunicación óptica"""
    kernel = np.array([[1, 0, 1],
                       [0, 1, 1],
                       [0, 1, 0]], dtype=np.uint8)
    
    gris = cv2.bilateralFilter(gris, 8, 170, 180)
    gris = cv2.medianBlur(gris, 3)
    #input("pausa")
    
    clahe = cv2.createCLAHE(clipLimit=4.3, tileGridSize=(4, 4))
    gris = clahe.apply(gris)
    gris = cv2.morphologyEx(gris, cv2.MORPH_CLOSE, kernel)
    
    gris = cv2.normalize(gris, None, 30, 124, cv2.NORM_MINMAX)
    
    return gris



def recortar_pantalla(frame, pantalla_contorno, size=200):
    """Recorta y rectifica la pantalla"""
    if pantalla_contorno is None:
        return frame
    
    pts = pantalla_contorno.reshape(4, 2)
    
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    dst = np.array([[0, 0], [size-1, 0], [size-1, size-1], [0, size-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    recortada = cv2.warpPerspective(frame, M, (size, size))
    
    return recortada


def encontrar_bandera_windows(diff, area_min=10000, area_max=50000):
    """Encuentra la bandera (logo Windows 11) en la imagen diff"""
    if diff is None:
        return None, 0, 0

    if len(diff.shape) == 3:
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    h, w = diff.shape
    area_total = h * w
    
    kernel = np.ones((4, 4), np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, 0, 0

    mejor = None
    mejor_area = 0
    mejor_proporcion = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        proporcion = area / area_total

        if proporcion < 0.20 or proporcion > 0.50:
            continue
        if area < area_min or area > area_max:
            continue

        if area > mejor_area:
            mejor_area = area
            mejor_proporcion = proporcion
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int32(box)
            mejor = box.reshape(-1, 1, 2)

    if mejor is not None:
        print(f"🪟 Bandera Windows | área:{mejor_area:.0f} | {mejor_proporcion:.1%}")
    
    return mejor, mejor_area, mejor_proporcion


# ==================================================
# MAQUINA DE ESTADOS
# ==================================================
ESTADO_ESPERANDO_BANDERA = 0
ESTADO_ESPERANDO_3_PULSOS = 1
ESTADO_RECIBIENDO = 2

estado_actual = ESTADO_ESPERANDO_BANDERA
pulsos_detectados = 0
frames_datos = []
mensaje_completo = ""
ultimo_score = 0
cuadrado_capturado = None
bandera_detectada = False
binaria_recortada_mostrar = None

print("\n" + "="*50)
print("🎯 RECEPTOR OPTICO")
print("📡 Buscando bandera Windows 11 en RESTA...")
print("="*50)
print("-"*50 + "\n")

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    roi = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]
    roi = cv2.resize(roi, ROI_SIZE)
    gris = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    if USE_OTSU:
        gris_eq = equalizar(gris)
        _, binaria = cv2.threshold(gris_eq, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, binaria = cv2.threshold(gris, THRESHOLD_BINARIO, 255, cv2.THRESH_BINARY)
    
    kernel = np.ones((2, 2), np.uint8)
    binaria = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, kernel)
    
    score, diff = detectar_cambio(binaria)
    
    # Detectar bandera en DIFF
    cuadrado_bandera, area_bandera, proporcion = encontrar_bandera_windows(diff, area_min=8000, area_max=40000)
    es_bandera = cuadrado_bandera is not None and 0.20 < proporcion < 0.50
    
    # Detectar flanco de pulso
    es_pulso = False
    if score > CAMBIO_MINIMO and ultimo_score <= CAMBIO_MINIMO:
        es_pulso = True
        print(f"⚡ Flanco | score:{score}")
    
    # ==================================================
    # MAQUINA DE ESTADOS
    # ==================================================
    
    if estado_actual == ESTADO_ESPERANDO_BANDERA:
        if es_bandera and not bandera_detectada:
            cuadrado_capturado = cuadrado_bandera
            bandera_detectada = True
            estado_actual = ESTADO_ESPERANDO_3_PULSOS
            pulsos_detectados = 0
            print("\n" + "="*50)
            print("🪟 ¡BANDERA WINDOWS DETECTADA!")
            print(f"   Área: {area_bandera:.0f} px | {proporcion:.1%}")
            print("="*50)
            print("🔍 Esperando 3 pulsos...")
            print("-"*50)
    
    elif estado_actual == ESTADO_ESPERANDO_3_PULSOS:
        if es_pulso:
            pulsos_detectados += 1
            print(f"⚡ Pulso #{pulsos_detectados}")
            if pulsos_detectados >= 3:
                estado_actual = ESTADO_RECIBIENDO
                print("\n🎬 ¡3 pulsos! Iniciando recepción...")
                print("-"*50)
    
    elif estado_actual == ESTADO_RECIBIENDO:
        if es_pulso and cuadrado_capturado is not None:
            # Recortar usando BINARIA (no diff)
            esquinas_ordenadas = ordenar_esquinas(cuadrado_capturado.reshape(4, 2))
            pantalla_recortada = recortar_pantalla(roi, esquinas_ordenadas)
            gris_recortada = cv2.cvtColor(pantalla_recortada, cv2.COLOR_BGR2GRAY)
            _, binaria_recortada = cv2.threshold(gris_recortada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            binaria_recortada_mostrar = erosionar_bits(binaria_recortada, kernel_size=2, iteraciones=1)
            
            bits, texto, bytes_data = demodular_frame(binaria_recortada_mostrar)
            
            if texto and texto.strip():
                frames_datos.append(texto)
                mensaje_completo += texto
                print(f"📥 DATA[{len(frames_datos)}]: '{texto}'")
    
    ultimo_score = score
    
    # ==================================================
    # VISUALIZACION
    # ==================================================
    debug = roi.copy()
    
    estados = ["BUSCANDO BANDERA", "3 PULSOS", "RECIBIENDO"]
    cv2.putText(debug, f"{estados[estado_actual]}", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
    cv2.putText(debug, f"S={score}", (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    if estado_actual == ESTADO_ESPERANDO_3_PULSOS:
        cv2.putText(debug, f"PULSOS: {pulsos_detectados}/3", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    if cuadrado_capturado is not None:
        cv2.drawContours(debug, [cuadrado_capturado], -1, (0, 255, 255), 3)
        cv2.putText(debug, "BANDERA", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    cv2.imshow("RECEPTOR", debug)
    cv2.imshow("BINARIA", binaria)
    
    # MOSTRAR BINARIA RECORTADA (dónde se buscan los bits)
    if binaria_recortada_mostrar is not None:
        cv2.imshow("BINARIA_RECORTADA", binaria_recortada_mostrar)
    
    if diff is not None:
        resta_display = cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)
        if cuadrado_bandera is not None:
            cv2.drawContours(resta_display, [cuadrado_bandera], -1, (0, 0, 255), 3)
            cv2.putText(resta_display, f"BANDERA", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imshow("RESTA", resta_display)
    
    if cv2.waitKey(30) & 0xFF == 27:
        break

print(f"\n📝 MENSAJE FINAL: {mensaje_completo}")
cap.release()
cv2.destroyAllWindows()
