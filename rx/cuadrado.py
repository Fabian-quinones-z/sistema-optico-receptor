#cuadrado
import cv2
import numpy as np


def buscar_cuadrado_perfecto(binaria, tolerancia_angular=5, tolerancia_lados=0.15):
    """
    Busca un cuadrado casi perfecto usando PDI clásica
    
    Parámetros:
    - tolerancia_angular: grados de desviación permitidos (ángulos deben ser ~90°)
    - tolerancia_lados: proporción de diferencia entre lados permitida
    """
    # Encontrar contornos
    contours, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    cuadrados = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:  # Muy pequeño
            continue
        
        # Aproximar polígono
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.01 * peri, True)  # Más preciso (0.01)
        
        # Debe tener 4 lados
        if len(approx) != 4:
            continue
        
        # ==========================================
        # VERIFICACIONES DE CUADRADO PERFECTO
        # ==========================================
        
        # 1. Obtener puntos y lados
        pts = approx.reshape(4, 2)
        
        # Calcular longitudes de los 4 lados
        lados = []
        for i in range(4):
            x1, y1 = pts[i]
            x2, y2 = pts[(i+1) % 4]
            lado = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            lados.append(lado)
        
        # Calcular ángulos internos
        angulos = []
        for i in range(4):
            p1 = pts[i]
            p2 = pts[(i+1) % 4]
            p3 = pts[(i+2) % 4]
            
            v1 = (p1[0] - p2[0], p1[1] - p2[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            
            producto_punto = v1[0]*v2[0] + v1[1]*v2[1]
            magnitud1 = np.sqrt(v1[0]**2 + v1[1]**2)
            magnitud2 = np.sqrt(v2[0]**2 + v2[1]**2)
            
            if magnitud1 * magnitud2 > 0:
                angulo = np.arccos(producto_punto / (magnitud1 * magnitud2))
                angulo_grados = np.degrees(angulo)
                angulos.append(angulo_grados)
        
        # 2. Verificar ángulos (deben ser ~90°)
        angulos_correctos = all(abs(a - 90) < tolerancia_angular for a in angulos)
        
        # 3. Verificar lados opuestos iguales (rectángulo)
        lado_opuesto1 = abs(lados[0] - lados[2]) / max(lados[0], lados[2]) if max(lados[0], lados[2]) > 0 else 0
        lado_opuesto2 = abs(lados[1] - lados[3]) / max(lados[1], lados[3]) if max(lados[1], lados[3]) > 0 else 0
        
        # 4. Verificar lados adyacentes similares (cuadrado casi perfecto)
        lado_adyacente1 = abs(lados[0] - lados[1]) / max(lados[0], lados[1]) if max(lados[0], lados[1]) > 0 else 0
        lado_adyacente2 = abs(lados[1] - lados[2]) / max(lados[1], lados[2]) if max(lados[1], lados[2]) > 0 else 0
        
        # 5. Calcular qué tan rectangular es (solidity)
        rect = cv2.minAreaRect(cnt)
        rect_area = rect[1][0] * rect[1][1]
        solidity = area / rect_area if rect_area > 0 else 0
        
        # Criterios de cuadrado casi perfecto
        es_cuadrado = (
            angulos_correctos and
            lado_opuesto1 < tolerancia_lados and
            lado_opuesto2 < tolerancia_lados and
            lado_adyacente1 < tolerancia_lados * 1.5 and
            lado_adyacente2 < tolerancia_lados * 1.5 and
            solidity > 0.85  # Muy rectangular
        )
        
        if es_cuadrado:
            cuadrados.append((approx, area, solidity, lados, angulos))
    
    if not cuadrados:
        return None
    
    # Ordenar por área (el más grande primero)
    cuadrados.sort(key=lambda x: x[1], reverse=True)
    mejor_cuadrado = cuadrados[0][0]
    
    return mejor_cuadrado


def buscar_cuadrado_por_relacion_aspecto(binaria, tolerancia_ratio=0.1):
    """
    Busca cuadrados por relación de aspecto (lado1/lado2 ≈ 1)
    """
    contours, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    cuadrados = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue
        
        # Obtener rectángulo rotado mínimo
        rect = cv2.minAreaRect(cnt)
        width = rect[1][0]
        height = rect[1][1]
        
        if width == 0 or height == 0:
            continue
        
        # Relación de aspecto (debe ser cercana a 1)
        aspect_ratio = max(width, height) / min(width, height)
        
        # Verificar que sea casi cuadrado
        if abs(aspect_ratio - 1) < tolerancia_ratio:
            # Aproximar polígono
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            
            if len(approx) == 4:
                cuadrados.append((approx, area, aspect_ratio))
    
    if not cuadrados:
        return None
    
    cuadrados.sort(key=lambda x: x[1], reverse=True)
    return cuadrados[0][0]


def buscar_cuadrado_por_contorno_mas_grande(binaria, area_minima=1000):
    """
    Encuentra el contorno más grande que sea cuadrilátero
    """
    contours, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Ordenar por área descendente
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < area_minima:
            continue
        
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.01 * peri, True)  # Más preciso
        
        if len(approx) == 4:
            # Verificar que no sea demasiado deformado
            rect = cv2.minAreaRect(cnt)
            rect_area = rect[1][0] * rect[1][1]
            
            if rect_area > 0:
                solidity = area / rect_area
                if solidity > 0.85:  # Solo contornos muy rectangulares
                    return approx
    
    return None


def buscar_cuadrado_por_momentos(binaria):
    """
    Usa momentos de Hu para identificar cuadrados
    """
    contours, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue
        
        # Calcular momentos de Hu (invariantes a rotación/escala)
        moments = cv2.moments(cnt)
        hu_moments = cv2.HuMoments(moments).flatten()
        
        # Los momentos de Hu para un cuadrado tienen características específicas
        # El primer momento (hu[0]) es muy pequeño para formas simétricas
        # hu[0] cerca de 0 indica simetría
        
        if abs(hu_moments[0]) < 0.1:  # Muy simétrico
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            
            if len(approx) == 4:
                return approx
    
    return None



def capturar_cuadrado(diff):
    """Captura el cuadrado de la imagen diff y retorna las 4 esquinas"""
    if diff is None:
        return None
    
    contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    cnt = max(contours, key=cv2.contourArea)
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    
    if len(approx) == 4:
        return approx
    return None



def encontrar_cuadrado_mas_grande(
        diff,
        area_min=500,
        area_max=50000):

    if diff is None:
        return None, 0

    if len(diff.shape) == 3:
        diff = cv2.cvtColor(
            diff,
            cv2.COLOR_BGR2GRAY
        )

    # cerrar huecos
    kernel = np.ones((5,5), np.uint8)

    diff = cv2.morphologyEx(
        diff,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    contours, _ = cv2.findContours(
        diff,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None, 0

    mejor = None
    mejor_area = 0

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area < area_min:
            continue

        if area > area_max:
            continue

        if area > mejor_area:

            mejor_area = area

            rect = cv2.minAreaRect(cnt)

            box = cv2.boxPoints(rect)

            box = np.int32(box)

            mejor = box.reshape(
                -1,
                1,
                2
            )

    return mejor, mejor_area

def ordenar_esquinas(pts):
    """Ordena las esquinas: superior-izq, superior-der, inferior-der, inferior-izq"""
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    
    rect[0] = pts[np.argmin(s)]   # Superior-izquierdo
    rect[2] = pts[np.argmax(s)]   # Inferior-derecho
    rect[1] = pts[np.argmin(diff)] # Superior-derecho
    rect[3] = pts[np.argmax(diff)] # Inferior-izquierdo
    
    return rect



def recortar_pantalla(frame, esquinas, size=200):
    """Recorta y rectifica la pantalla usando las esquinas ordenadas"""
    if esquinas is None:
        return frame
    
    dst = np.array([[0, 0], [size-1, 0], [size-1, size-1], [0, size-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(esquinas, dst)
    recortada = cv2.warpPerspective(frame, M, (size, size))
    
    return recortada


# En diff, la bandera aparece como un CUADRADO BLANCO SÓLIDO
# Porque el cambio de negro a blanco es TOTAL

def es_bandera_valida(cuadrado, area, diff_shape):
    """Valida que el cuadrado sea la bandera (logo Windows 11)"""
    h, w = diff_shape
    
    # 1. Área debe ser significativa (>10% del frame)
    proporcion = area / (h * w)
    
    # 2. La bandera ocupa aproximadamente 25-40% del área cuando aparece
    return 0.20 < proporcion < 0.50
