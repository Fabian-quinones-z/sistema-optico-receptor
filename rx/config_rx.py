#config_rx.py

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

CAMBIO_MINIMO = 300

# ==================================================
# CONFIGURAR VISUALIZACION
# ==================================================

MOSTRAR_FRAME = False
MOSTRAR_BINARIA = True
MOSTRAR_LINEAS = False
MOSTRAR_DIFF = True
MOSTRAR_RECTIFICADA = True
