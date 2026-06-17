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






#########Proyectar###############
import cv2
import numpy as np

def crear_panel_control(debug, binaria, diff_mov, lienzo_referencia, resta_canal, 
                        roi_lienzo, roi_estable, sync_realizado, contadorframes, score):
    """
    Crea un panel de control con múltiples vistas en una sola ventana
    """
    # Obtener dimensiones de las imágenes
    h_debug, w_debug = debug.shape[:2]
    h_bin, w_bin = binaria.shape[:2]
    
    # Dimensiones de las miniaturas (escaladas)
    thumb_size = (320, 240)  # ancho, alto
    
    # 1. Redimensionar todas las imágenes al mismo tamaño
    debug_thumb = cv2.resize(debug, thumb_size)
    binaria_thumb = cv2.resize(binaria, thumb_size)
    
    # 2. Crear panel principal (2 filas x 3 columnas)
    # Fila 1: RECEPTOR | BINARIA | MOVIMIENTO
    # Fila 2: LIENZO REF | RESTA | INFO
    
    # Convertir imágenes a color si están en escala de grises
    if len(binaria_thumb.shape) == 2:
        binaria_thumb = cv2.cvtColor(binaria_thumb, cv2.COLOR_GRAY2BGR)
    
    # Preparar MOVIMIENTO
    if diff_mov is not None:
        mov_thumb = cv2.resize(diff_mov, thumb_size)
        if len(mov_thumb.shape) == 2:
            mov_thumb = cv2.cvtColor(mov_thumb, cv2.COLOR_GRAY2BGR)
    else:
        mov_thumb = np.zeros((thumb_size[1], thumb_size[0], 3), dtype=np.uint8)
        cv2.putText(mov_thumb, "SIN MOVIMIENTO", (50, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    
    # Preparar LIENZO REFERENCIA
    if sync_realizado and lienzo_referencia is not None:
        ref_thumb = cv2.resize(lienzo_referencia, thumb_size)
        if len(ref_thumb.shape) == 2:
            ref_thumb = cv2.cvtColor(ref_thumb, cv2.COLOR_GRAY2BGR)
    else:
        ref_thumb = np.zeros((thumb_size[1], thumb_size[0], 3), dtype=np.uint8)
        cv2.putText(ref_thumb, "ESPERANDO SYNC...", (50, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    
    # Preparar RESTA
    if sync_realizado and resta_canal is not None and resta_canal.size > 0:
        resta_thumb = cv2.resize(resta_canal, thumb_size)
        if len(resta_thumb.shape) == 2:
            resta_thumb = cv2.cvtColor(resta_thumb, cv2.COLOR_GRAY2BGR)
    else:
        resta_thumb = np.zeros((thumb_size[1], thumb_size[0], 3), dtype=np.uint8)
        cv2.putText(resta_thumb, "SIN DIFERENCIA", (50, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    
    # 3. Crear panel de información (INFO)
    info_panel = np.zeros((thumb_size[1], thumb_size[0], 3), dtype=np.uint8)
    info_panel[:] = (30, 30, 30)  # Fondo gris oscuro
    
    # Título
    cv2.putText(info_panel, "=== PANEL DE CONTROL ===", (30, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Información del sistema
    y_pos = 70
    cv2.putText(info_panel, f"Frame: {contadorframes}", (30, y_pos), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    y_pos += 30
    cv2.putText(info_panel, f"Score: {score:.1f}", (30, y_pos), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    y_pos += 30
    estado_sync = "SYNC OK" if sync_realizado else "SYNC OFF"
    color_sync = (0, 255, 0) if sync_realizado else (0, 0, 255)
    cv2.putText(info_panel, f"Estado: {estado_sync}", (30, y_pos), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_sync, 1)
    
    # Información de ROI
    if roi_lienzo is not None:
        x, y, w, h = roi_lienzo
        y_pos += 30
        cv2.putText(info_panel, f"ROI: ({x},{y}) {w}x{h}", (30, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        
        y_pos += 30
        cv2.putText(info_panel, f"Area: {w*h} px", (30, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        
        y_pos += 30
        cv2.putText(info_panel, f"Estabilidad: {roi_estable}/3", (30, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        
        # Barra de progreso de estabilidad
        bar_x, bar_y = 30, y_pos + 15
        bar_w, bar_h = 200, 15
        cv2.rectangle(info_panel, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), 
                     (50, 50, 50), -1)
        fill_w = int((roi_estable / 3) * bar_w)
        color_barra = (0, 255, 0) if roi_estable >= 3 else (0, 255, 255)
        cv2.rectangle(info_panel, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), 
                     color_barra, -1)
    
    # 4. Crear el grid del panel de control
    # Espaciado entre imágenes
    spacing = 5
    panel_width = thumb_size[0] * 3 + spacing * 4
    panel_height = thumb_size[1] * 2 + spacing * 3 + 40  # +40 para título
    
    # Crear panel completo
    panel = np.zeros((panel_height, panel_width, 3), dtype=np.uint8)
    panel[:] = (20, 20, 20)  # Fondo gris muy oscuro
    
    # Título del panel
    cv2.putText(panel, "CONTROL PANEL - OPTICAL MODEM", (10, 25), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    # Posiciones de las imágenes
    x_offset = spacing
    y_offset = 40
    
    # Fila 1
    posiciones = [
        (x_offset, y_offset, "RECEPTOR", debug_thumb),
        (x_offset + thumb_size[0] + spacing, y_offset, "BINARIA", binaria_thumb),
        (x_offset + (thumb_size[0] + spacing) * 2, y_offset, "MOVIMIENTO", mov_thumb)
    ]
    
    # Fila 2
    y_offset2 = y_offset + thumb_size[1] + spacing
    posiciones.extend([
        (x_offset, y_offset2, "LIENZO REF", ref_thumb),
        (x_offset + thumb_size[0] + spacing, y_offset2, "RESTA", resta_thumb),
        (x_offset + (thumb_size[0] + spacing) * 2, y_offset2, "INFO", info_panel)
    ])
    
    # Colocar imágenes en el panel
    for x, y, titulo, img in posiciones:
        # Copiar imagen
        panel[y:y+thumb_size[1], x:x+thumb_size[0]] = img
        
        # Borde de la imagen
        cv2.rectangle(panel, (x-1, y-1), (x+thumb_size[0]+1, y+thumb_size[1]+1), 
                     (60, 60, 60), 1)
        
        # Título de la imagen (fondo oscuro semitransparente)
        titulo_y = y + 25
        cv2.rectangle(panel, (x, titulo_y-18), (x + len(titulo)*8 + 10, titulo_y+2), 
                     (0, 0, 0, 0.7), -1)
        cv2.putText(panel, titulo, (x+5, titulo_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    # 5. Agregar barra de estado inferior
    status_y = panel_height - 25
    cv2.rectangle(panel, (0, status_y-5), (panel_width, panel_height), (40, 40, 40), -1)
    
    # Indicador de estado de ROI en la barra
    if roi_lienzo is not None:
        cv2.putText(panel, f"ROI ACTIVA: {w}x{h}", (10, status_y+5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    else:
        cv2.putText(panel, "ROI INACTIVA - BUSCANDO...", (10, status_y+5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    # Indicador de sync
    if sync_realizado:
        cv2.putText(panel, "SYNC: ACTIVO", (panel_width-150, status_y+5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    else:
        cv2.putText(panel, "SYNC: INACTIVO", (panel_width-150, status_y+5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    return panel
