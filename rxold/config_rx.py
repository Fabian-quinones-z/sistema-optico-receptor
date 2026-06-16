# ==================================================
# CONFIGURACION GENERAL
# ==================================================

VIDEO_FILE = "docs/muestra.mp4"

# ROI
ROI_X1 = 200
ROI_Y1 = 50

ROI_X2 = 700
ROI_Y2 = 550

# Tamaño interno
ROI_SIZE = (200, 200)

# ==================================================
# CONFIGURAR THRESHOLD BINARIO
# ==================================================

USE_OTSU = True
THRESHOLD_BINARIO = 128

# ==================================================
# CONFIGURAR DETECCION DE BANDERAS
# ==================================================

CAMBIO_MINIMO = 8000  # Ajusta este valor según veas los pulsos blancos
                     # Si no detecta pulsos, baja el valor (ej: 200)
                     # Si detecta falsos, sube el valor (ej: 500)

# ==================================================
# CONFIGURAR VISUALIZACION
# ==================================================

MOSTRAR_FRAME = True
MOSTRAR_BINARIA = True
MOSTRAR_LINEAS = False
MOSTRAR_DIFF = True
MOSTRAR_RECTIFICADA = True

# ==================================================
# CONFIGURACION DE DEMODULACION
# ==================================================

MIN_CONTOUR_AREA = 500
#GRID_SIZE = 8
