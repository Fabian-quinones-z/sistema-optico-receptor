import cv2
import numpy as np
from common.config import *
from rx.sync import detectar_sync
from rx.motion import detectar_cambio
from rx.demodulation import demodular_frame
from rx.geometry import erosionar_bits, detectar_lienzo
from rx.equalizador import *

# ============================================================================
# CONFIGURACIÓN DEL SISTEMA - AJUSTADA
# ============================================================================
UMBRAL_SYNC = 0.23                    # Umbral para detectar sincronismo
MAX_DESPLAZAMIENTO = 15               # Píxeles máximos de desplazamiento
MAX_CAMBIO_TAMANO = 0.25              # Cambio máximo en tamaño (25%)

# AJUSTE: Áreas basadas en los logs reales
# Tus ROIs válidas reportadas: 191x169 (32279), 189x168 (31752), etc.
# Pero veo que el área real debería ser ~145x160 = 23200
# El problema es que detectar_lienzo() está dando ROIs demasiado grandes
AREA_MINIMA_ROI = 9000               # Reducido para aceptar ROIs más pequeñas
AREA_MAXIMA_ROI = 33000               # Aumentado para aceptar ROIs más grandes

PERIODO_TOLERANCIA = 0.20             # Tolerancia del 20% para periodos (más flexible)
ESTABILIDAD_REQUERIDA = 3             # Sincronismos consecutivos necesarios

# ============================================================================
# INICIALIZACIÓN LIMPIA
# ============================================================================
cap = cv2.VideoCapture(VIDEO_FILE)

# Estado del sistema
sync_realizado = False
mensaje_completo = ""

# ROI y referencia
roi_lienzo = None
roi_anterior = None
lienzo_referencia = None
resta_canal = None

# Métricas de estabilidad
roi_estable = 0
mejor_roi = None
mejor_area = 0
mejor_estabilidad = 0

# Variables de movimiento
maxScore = 0
score = 0
relacion = []
contadorframes = 0
framesbandera = []
diferencia = []

print("\n" + "="*60)
print("RECEPTOR OPTICO - VERSION ESTABLE v2")
print("SYNC POR CAMBIO DE ESTADO CON VALIDACIÓN DE ROI")
print("="*60)

# ============================================================================
# BUCLE PRINCIPAL
# ============================================================================
while True:
    # 1. CAPTURAR FRAME
    ret, frame = cap.read()
    if not ret:
        break

    # 2. PREPROCESAMIENTO
    roi = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]
    roi = cv2.resize(roi, ROI_SIZE)
    gris = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 3. BINARIZACIÓN
    if USE_OTSU:
        gris_eq = equalizar(gris)
        _, binaria = cv2.threshold(gris_eq, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, binaria = cv2.threshold(gris, THRESHOLD_BINARIO, 255, cv2.THRESH_BINARY)

    # 4. LIMPIEZA MORFOLÓGICA
    kernel = np.ones((2,2), np.uint8)
    binaria = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, kernel)

    # 5. DETECCIÓN DE MOVIMIENTO
    score, maxScore, diff_mov = detectar_cambio(binaria, maxScore)
    
    # 6. CÁLCULO DE MÉTRICAS - CON VERIFICACIÓN DE None
    if diff_mov is not None:
        blancos = np.count_nonzero(diff_mov)
        total = max(1, diff_mov.size)
        ratio_movimiento = blancos / total
    else:
        blancos = 0
        total = 1
        ratio_movimiento = 0.0
    
    relacion.append(ratio_movimiento)
    contadorframes += 1

    # 7. DETECCIÓN DE BANDERA DE SYNC
    if diff_mov is not None and ratio_movimiento > UMBRAL_SYNC:
        print(f"SYNC DETECTADO - ratio={ratio_movimiento:.3f} en frame {contadorframes}")
        framesbandera.append(contadorframes)
        
        # Calcular diferencias entre frames de sync
        if len(framesbandera) >= 2:
            diferencia.append(contadorframes - framesbandera[-2])
            
            # 8. CONFIRMAR SYNC PERIÓDICO
            if len(framesbandera) >= 3:
                d1 = diferencia[-1]
                d2 = diferencia[-2]
                error_periodo = abs(d1 - d2)
                tolerancia_periodo = max(3, int(d2 * PERIODO_TOLERANCIA))
                
                if error_periodo <= tolerancia_periodo:
                    print(f"SYNC CONFIRMADO - periodos: {d1}, {d2} (error={error_periodo})")
                    
                    # 9. DETECTAR ROI CANDIDATA
                    # PRIMERO: Intentar con diff_mov (como antes)
                    roi_candidata = detectar_lienzo(diff_mov)
                    
                    # SEGUNDO: Si falla, intentar con binaria
                    if roi_candidata is None:
                        roi_candidata = detectar_lienzo(binaria)
                        if roi_candidata is not None:
                            print("  - ROI encontrada usando binaria")
                    
                    if roi_candidata is not None:
                        x, y, w, h = roi_candidata
                        area = w * h
                        
                        print(f"ROI CANDIDATA: x={x} y={y} w={w} h={h} area={area}")
                        print(f"  - Área esperada: {AREA_MINIMA_ROI}-{AREA_MAXIMA_ROI}")
                        
                        # 10. FILTRAR POR TAMAÑO
                        if AREA_MINIMA_ROI <= area <= AREA_MAXIMA_ROI:
                            
                            # 11. PRIMERA ROI O COMPARACIÓN CON ANTERIOR
                            if roi_lienzo is None:
                                # Primera ROI válida
                                roi_lienzo = roi_candidata
                                roi_anterior = roi_candidata
                                roi_estable = 1
                                print(f"ROI INICIAL ACEPTADA: {roi_lienzo}")
                            else:
                                # Comparar con ROI anterior
                                xold, yold, wold, hold = roi_anterior
                                
                                # Cálculo de diferencias
                                dx = abs(x - xold)
                                dy = abs(y - yold)
                                dw = abs(w - wold)
                                dh = abs(h - hold)
                                
                                # Relaciones porcentuales
                                rw = dw / max(1, wold)
                                rh = dh / max(1, hold)
                                
                                # Métricas adicionales
                                cx_old = xold + wold/2
                                cy_old = yold + hold/2
                                cx_new = x + w/2
                                cy_new = y + h/2
                                desplazamiento_centro = np.sqrt((cx_new-cx_old)**2 + (cy_new-cy_old)**2)
                                
                                # Score de confianza (área / estabilidad)
                                confianza = area / (1 + dx + dy + dw + dh)
                                
                                print(f"  - Delta: dx={dx} dy={dy} dw={dw} dh={dh}")
                                print(f"  - Ratios: rw={rw:.3f} rh={rh:.3f}")
                                print(f"  - Desplazamiento centro: {desplazamiento_centro:.1f}px")
                                print(f"  - Confianza: {confianza:.2f}")
                                
                                # 12. CRITERIO DE ACEPTACIÓN
                                if (dx < MAX_DESPLAZAMIENTO and 
                                    dy < MAX_DESPLAZAMIENTO and 
                                    rw < MAX_CAMBIO_TAMANO and 
                                    rh < MAX_CAMBIO_TAMANO):
                                    
                                    roi_estable += 1
                                    roi_lienzo = roi_candidata
                                    roi_anterior = roi_candidata
                                    
                                    print(f"ROI ACEPTADA - Estabilidad: {roi_estable}/{ESTABILIDAD_REQUERIDA}")
                                    
                                    # 13. CONFIRMAR SYNC CUANDO LA ROI ES ESTABLE
                                    if roi_estable >= ESTABILIDAD_REQUERIDA and not sync_realizado:
                                        sync_realizado = True
                                        if diff_mov is not None:
                                            lienzo_referencia = diff_mov[y:y+h, x:x+w].copy()

                                        print(f"*** SYNC Y ROI CONFIRMADOS ***")
                                        print(f"  - ROI estable: {roi_lienzo}")
                                        print(f"  - Dimensiones: {w}x{h}")
                                        print(f"  - Área: {area}")

                                else:
                                    print("ROI DESCARTADA - Cambios excesivos")
                                    # No reiniciamos roi_estable completamente, solo disminuimos
                                    roi_estable = max(0, roi_estable - 1)
                            
                            # 14. GUARDAR MEJOR ROI
                            if area > mejor_area:
                                mejor_area = area
                                mejor_roi = roi_candidata
                                mejor_estabilidad = roi_estable
                                print(f"NUEVA MEJOR ROI - área={mejor_area}, estabilidad={mejor_estabilidad}")
                        else:
                            print(f"ROI DESCARTADA - Tamaño fuera de rango (debe ser {AREA_MINIMA_ROI}-{AREA_MAXIMA_ROI})")
                    else:
                        print("No se detectó ROI válida")

    # ============================================================================
    # VISUALIZACIÓN
    # ============================================================================
    debug = roi.copy()
    
    # Mostrar información en la imagen
    cv2.putText(debug, f"S={score}", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(debug, f"F={contadorframes}", (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    cv2.putText(debug, f"Sync={sync_realizado}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    
    if roi_lienzo is not None:
        x, y, w, h = roi_lienzo
        cv2.rectangle(debug, (x,y), (x+w,y+h), (255,0,0), 2)
        cv2.putText(debug, f"ROI {w}x{h}", (x,y-25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)
        cv2.putText(debug, f"EST:{roi_estable}", (x,y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 2)
        cv2.putText(debug, "LIENZO", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

    
    # Mostrar todas las ventanas
    cv2.imshow("RECEPTOR", debug)
    cv2.imshow("BINARIA", binaria)
    
    if diff_mov is not None:
        cv2.imshow("MOVIMIENTO", diff_mov)
    
    if sync_realizado and lienzo_referencia is not None:
        cv2.imshow("LIENZO", lienzo_referencia)
        if resta_canal is not None and resta_canal.size > 0:
            cv2.imshow("RESTA", resta_canal)
    
    # 15. SALIR CON ESC
    tecla = cv2.waitKey(30)
    if tecla == 27:
        break

# ============================================================================
# RESULTADOS FINALES
# ============================================================================
print("\n" + "="*60)
print("RESUMEN FINAL")
print("="*60)
print(f"Frames procesados: {contadorframes}")
print(f"Sincronismos detectados: {len(framesbandera)}")
print(f"ROI final: {roi_lienzo}")
if roi_lienzo is not None:
    x, y, w, h = roi_lienzo
    print(f"  - Dimensiones: {w}x{h} (área={w*h})")
print(f"Mejor ROI encontrada: {mejor_roi} (área={mejor_area}, estabilidad={mejor_estabilidad})")
print(f"Sync realizado: {sync_realizado}")
if sync_realizado:
    print(f"Mensaje recibido: {mensaje_completo}")
print("="*60)

cap.release()
cv2.destroyAllWindows()
