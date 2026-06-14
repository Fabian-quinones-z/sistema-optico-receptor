import cv2
import numpy as np

# ==================================================
# DETECCION DE LINEAS Y ANGULOS
# ==================================================

def detectar_lineas(img):
    edges = cv2.Canny(img, 50, 150)
    return cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)


def angulo_dominante(lines):
    if lines is None:
        return 0

    angulos = []
    for l in lines:
        x1, y1, x2, y2 = l[0]
        angulo = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if abs(angulo) < 45:
            angulos.append(angulo)

    if len(angulos) == 0:
        return 0
    return np.median(angulos)


# ==================================================
# DETECCION DE PANTALLA (CUADRADO)
# ==================================================

def encontrar_pantalla_edges(edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1500:
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)

        if len(approx) == 4:
            return approx
    return None


def buscar_cuadrado_por_contorno_mas_grande(binaria, area_minima=1000, solidity_minima=0.85):
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
        approx = cv2.approxPolyDP(cnt, 0.01 * peri, True)
        
        if len(approx) == 4:
            # Verificar solidez
            rect = cv2.minAreaRect(cnt)
            rect_area = rect[1][0] * rect[1][1]
            
            if rect_area > 0:
                solidity = area / rect_area
                if solidity > solidity_minima:
                    return approx
    
    return None


# ==================================================
# ELIMINACION DE LINEAS
# ==================================================

def eliminar_lineas_verticales(binaria, umbral=0.70):
    """Elimina líneas verticales contando píxeles blancos por columna"""
    resultado = binaria.copy()
    h, w = resultado.shape
    umbral_pixeles = int(h * umbral)

    for x in range(w):
        blancos = np.count_nonzero(resultado[:, x])
        if blancos > umbral_pixeles:
            resultado[:, x] = 0
    return resultado


def eliminar_lineas_horizontales(binaria, umbral=0.70):
    """Elimina líneas horizontales contando píxeles blancos por fila"""
    resultado = binaria.copy()
    h, w = resultado.shape
    umbral_pixeles = int(w * umbral)

    for y in range(h):
        blancos = np.count_nonzero(resultado[y, :])
        if blancos > umbral_pixeles:
            resultado[y, :] = 0
    return resultado


def eliminar_lineas_horizontales_verticales(binaria):
    """Elimina líneas horizontales y verticales"""
    resultado = eliminar_lineas_horizontales(binaria)
    resultado = eliminar_lineas_verticales(resultado)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    resultado = cv2.morphologyEx(resultado, cv2.MORPH_CLOSE, kernel)
    
    return resultado


# ==================================================
# DETECCION DE CUADRADO EN RESTA (PULSOS)
# ==================================================

def encontrar_cuadrado_en_resta(diff, area_minima=200, area_maxima=5000, solidity_minima=0.3):
    """
    Busca el cuadrado más grande en la imagen de diferencia (RESTA)
    Retorna el contorno del cuadrado y su área
    
    Parámetros:
    - area_minima: área mínima del cuadrado (200 por defecto)
    - area_maxima: área máxima del cuadrado (5000 por defecto)
    - solidity_minima: 0.6 es más tolerante que 0.7
    """

    # Encontrar contornos
    contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, 0
    
    cuadrados = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # Filtrar por área
        if area < area_minima or area > area_maxima:
            continue
        
        # Aproximar polígono con diferentes precisiones
        peri = cv2.arcLength(cnt, True)
        
        # Probar con diferentes precisiones
        for epsilon in [0.01, 0.02, 0.03, 0.04, 0.05]:
            approx = cv2.approxPolyDP(cnt, epsilon * peri, True)
            if len(approx) == 4:
                break
        else:
            continue  # No se encontró cuadrilátero
        
        # Calcular solidez
        rect = cv2.minAreaRect(cnt)
        rect_area = rect[1][0] * rect[1][1]
        
        if rect_area > 0:
            solidity = area / rect_area
            
            # Verificar que sea suficientemente rectangular
            if solidity > solidity_minima:
                # Calcular relación de aspecto
                width = rect[1][0]
                height = rect[1][1]
                aspect_ratio = max(width, height) / min(width, height) if min(width, height) > 0 else 0
                
                # Verificar que no sea demasiado alargado
                if aspect_ratio < 3.0:  # Máximo 3:1
                    cuadrados.append((approx, area, solidity, aspect_ratio))
    
    if not cuadrados:
        return None, 0
    
    # Ordenar por área (el más grande primero)
    cuadrados.sort(key=lambda x: x[1], reverse=True)
    mejor_cuadrado, mejor_area, mejor_solidity, mejor_aspect = cuadrados[0]
    
    print(f"   📐 Cuadrado en RESTA | área:{mejor_area:.0f} | solidez:{mejor_solidity:.2f} | aspect:{mejor_aspect:.2f}")
    
    return mejor_cuadrado, mejor_area

# ==================================================
# OPERACIONES MORFOLOGICAS PARA BITS
# ==================================================

def erosionar_bits(binaria, kernel_size=2, iteraciones=1):
    """Erosiona la imagen binaria para limpiar ruido y separar bits"""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.erode(binaria, kernel, iterations=iteraciones)


def dilatar_bits(binaria, kernel_size=2, iteraciones=1):
    """Dilata la imagen binaria para recuperar bits erosionados"""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.dilate(binaria, kernel, iterations=iteraciones)


def limpiar_bits(binaria, erosionar=1, dilatar=1):
    """Limpia bits: erosiona para eliminar ruido, luego dilata para recuperar tamaño"""
    kernel = np.ones((2, 2), np.uint8)
    
    for _ in range(erosionar):
        binaria = cv2.erode(binaria, kernel)
    
    for _ in range(dilatar):
        binaria = cv2.dilate(binaria, kernel)
    
    return binaria


# ==================================================
# VALIDACION DE PULSO POR CUADRADO
# ==================================================

def es_pulso_valido_por_cuadrado(diff, score, area_minima=300, area_maxima=5000):
    """
    Valida pulso buscando un cuadrado en la imagen RESTA
    """
    if diff is None or score < 100:
        return False, None, 0
    
    cuadrado, area = encontrar_cuadrado_en_resta(diff, area_minima, area_maxima)
    
    if cuadrado is not None:
        return True, cuadrado, area
    
    return False, None, 0



def validar_patron_bandera(binaria_recuadro, grid_size=8):
    """
    Valida que el recuadro contenga el patrón de bandera SYNC
    Patrón esperado (4 blanco + 4 negro por fila):
    11110000
    11110000
    11110000
    11110000
    00001111
    00001111
    00001111
    00001111
    """
    if binaria_recuadro is None:
        return False, 0
    
    h, w = binaria_recuadro.shape
    cell_h = h // grid_size
    cell_w = w // grid_size
    
    # Muestrear grid 8x8
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    
    for i in range(grid_size):
        for j in range(grid_size):
            y1 = i * cell_h
            y2 = (i + 1) * cell_h
            x1 = j * cell_w
            x2 = (j + 1) * cell_w
            
            celda = binaria_recuadro[y1:y2, x1:x2]
            promedio = np.mean(celda)
            grid[i, j] = 1 if promedio > 127 else 0
    
    # Patrón esperado: primeras 4 filas: [1,1,1,1,0,0,0,0]
    #               últimas 4 filas: [0,0,0,0,1,1,1,1]
    
    # Verificar primeras 4 filas (deben tener 4 unos y 4 ceros)
    correcto = True
    for i in range(4):
        fila = grid[i]
        # Debe tener exactamente 4 unos en las primeras 4 columnas
        if not (np.all(fila[:4] == 1) and np.all(fila[4:] == 0)):
            correcto = False
            break
    
    # Verificar últimas 4 filas (deben tener 4 ceros y 4 unos)
    for i in range(4, 8):
        fila = grid[i]
        if not (np.all(fila[:4] == 0) and np.all(fila[4:] == 1)):
            correcto = False
            break
    
    # Calcular porcentaje de coincidencia
    if correcto:
        return True, 100
    else:
        # Calcular similitud parcial
        aciertos = 0
        for i in range(4):
            for j in range(4):
                if grid[i, j] == 1:
                    aciertos += 1
                if grid[i, j+4] == 0:
                    aciertos += 1
        for i in range(4, 8):
            for j in range(4):
                if grid[i, j] == 0:
                    aciertos += 1
                if grid[i, j+4] == 1:
                    aciertos += 1
        
        porcentaje = (aciertos / 64) * 100
        return False, porcentaje


def encontrar_mejor_recuadro_con_bandera(diff, binaria, area_minima=500, area_maxima=30000):
    """
    Encuentra el recuadro más grande que coincida con el patrón de bandera
    """
    if diff is None:
        return None, 0, 0
    
    if len(diff.shape) == 3:
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    
    _, diff = cv2.threshold(diff, 127, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, 0, 0
    
    resultados = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        if area < area_minima or area > area_maxima:
            continue
        
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        if len(approx) != 4:
            continue
        
        # Verificar solidez
        rect = cv2.minAreaRect(cnt)
        rect_area = rect[1][0] * rect[1][1]
        
        if rect_area <= 0:
            continue
        
        solidity = area / rect_area
        
        if solidity < 0.5:
            continue
        
        # Probar a recortar y validar patrón de bandera
        pts = approx.reshape(4, 2)
        
        # Ordenar puntos
        rect_ordered = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        diff_pts = np.diff(pts, axis=1)
        
        rect_ordered[0] = pts[np.argmin(s)]
        rect_ordered[2] = pts[np.argmax(s)]
        rect_ordered[1] = pts[np.argmin(diff_pts)]
        rect_ordered[3] = pts[np.argmax(diff_pts)]
        
        width = 200
        height = 200
        
        dst = np.array([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]], dtype="float32")
        M = cv2.getPerspectiveTransform(rect_ordered, dst)
        
        # Recortar usando la imagen binaria original
        if len(binaria.shape) == 2:
            recortada = cv2.warpPerspective(binaria, M, (width, height))
        else:
            recortada = cv2.warpPerspective(cv2.cvtColor(binaria, cv2.COLOR_BGR2GRAY), M, (width, height))
        
        # Validar patrón de bandera
        es_bandera, porcentaje = validar_patron_bandera(recortada)
        
        resultados.append((approx, area, solidity, porcentaje, es_bandera))
    
    if not resultados:
        return None, 0, 0
    
    # Priorizar los que tienen patrón de bandera, luego por área
    resultados.sort(key=lambda x: (x[4], x[1]), reverse=True)
    
    mejor_cuadrado, mejor_area, mejor_solidity, mejor_porcentaje, es_bandera = resultados[0]
    
    if es_bandera:
        print(f"   🏁 BANDERA ENCONTRADA! área:{mejor_area:.0f} | coincidencia:{mejor_porcentaje:.0f}%")
    else:
        print(f"   📐 Recuadro | área:{mejor_area:.0f} | coincidencia bandera:{mejor_porcentaje:.0f}%")
    
    return mejor_cuadrado, mejor_area, mejor_porcentaje




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
