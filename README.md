# Optical Modem

Sistema de comunicación óptica Screen-to-Camera (S2C) basado en transmisión de información digital mediante patrones luminosos mostrados en pantalla y capturados por una cámara convencional.

El sistema implementa sincronización visual, detección temporal de pulsos, localización automática del transmisor, rectificación geométrica y demodulación binaria para reconstrucción de mensajes.

# Resumen

El proyecto implementa un canal de comunicación óptica visible utilizando únicamente técnicas clásicas de visión por computador.

La información es codificada en matrices binarias mostradas en una pantalla y posteriormente recuperada mediante una cámara o un archivo de video.

El receptor fue diseñado para operar bajo:

iluminación ambiente variable
reflejos parciales
desenfoque moderado
bajo contraste
pérdida parcial de bordes
errores de captura por FPS limitados

La detección se basa principalmente en:

sincronización visual
detección temporal de movimiento
acumulación histórica de cambios
extracción robusta de contornos
rectificación mediante perspectiva

# Estado Actual

Implementado:

Generación de tramas 8x8.
64 bits por frame.
Conversión texto → bits.
Generación automática de múltiples frames.
Preámbulo y postámbulo de sincronización.
Reproducción visual de tramas.
Captura desde cámara o video.
Selección de ROI.
Ecualización adaptativa.
Binarización fija y OTSU.
Detección de sincronización.
Detección temporal de pulsos.
Acumulación histórica de movimiento.
Localización automática del transmisor.
Rectificación geométrica.
Extracción de regiones cuadradas.
Demodulación básica de bits.

Pendiente:

Corrección de errores.
Reed-Solomon.
CRC.
Seguimiento dinámico del transmisor.
Kalman Filter.
Sincronización automática avanzada.
Matrices 16x16 y 32x32.
Optimización para transmisión en tiempo real.

# Estructura del Proyecto

```

optical_modem/

├── common/
│ ├── coding.py
│ ├── config.py
│ └── utils.py
│
├── tx/
│ ├── transmitter.py
│ ├── frame_builder.py
│ ├── display.py
│ ├── control_frames.py
│ ├── modulation.py
│ └── protocol.py
│
├── rx/
│ ├── receiver.py
│ ├── sync.py
│ ├── motion.py
│ ├── geometry.py
│ ├── rectify.py
│ ├── demodulation.py
│ ├── signal.py
│ └── config_rx.py
│
├── scripts/
│ ├── roi.py
│ ├── detectar_pantalla.py
│ ├── rectificar.py
│ └── firma_horizontal.py
│
├── tests/
│
├── docs/
│ └── muestra.mp4
│
├── outputs/
│
└── run.py

```

# Protocolo de Transmisión

Cada trama contiene:

```

8 × 8 = 64 bits

```

equivalente a:

```

8 bytes por frame

```

# Patrones de Sincronización

Se utilizan dos patrones alternados.

SYNC_A

```

xo
ox

```

SYNC_B

```

ox
xo

```

donde:

```

o = blanco
x = negro

```

Cada cuadrante ocupa:

```

4 × 4 bits

```

Por tanto:

```

SYNC = 8 × 8 bits

```

# Estructura de una Transmisión

```

SYNC_A
SYNC_B
SYNC_A
SYNC_B

DATA
DATA
DATA
...

SYNC_A
SYNC_B
SYNC_A
SYNC_B

```

# Arquitectura General

```

MENSAJE
│
▼
TEXT_TO_BITS
│
▼
FRAME_BUILDER
│
▼
DISPLAY
│
▼
PANTALLA
│
▼
CÁMARA
│
▼
ROI
│
▼
GRIS
│
▼
CLAHE
│
▼
BINARIA
│
▼
DETECCIÓN TEMPORAL
│
▼
LOCALIZACIÓN
│
▼
RECTIFICACIÓN
│
▼
DEMODULACIÓN
│
▼
MENSAJE

```

# Pipeline del Transmisor

```

Mensaje
│
▼
text_to_bits()
│
▼
build_frame()
│
▼
frames[]
│
▼
transmit_frames()
│
▼
Pantalla

```

# Pipeline del Receptor

```

FRAME
│
▼
ROI
│
▼
GRIS
│
▼
CLAHE
│
▼
BINARIA
│
├── detectar_sync()
│
├── detectar_cambio()
│
├── detectar_lineas()
│
├── angulo_dominante()
│
└── rectify_frame()
│
▼
DEMODULADOR
│
▼
MENSAJE

```

# Preprocesamiento

Cada imagen es convertida inicialmente a escala de grises.

Posteriormente se aplica:

```

bilateralFilter()
medianBlur()
CLAHE()
normalize()

```

Objetivos:

reducción de ruido
preservación de bordes
compensación de iluminación
aumento de contraste local

# Ecualización Adaptativa

El receptor utiliza CLAHE.

```

Contrast Limited Adaptive Histogram Equalization

```

La ecualización local permite recuperar regiones deterioradas por:

brillo ambiente
reflejos
iluminación desigual
saturación parcial

Proceso:

```

gris
↓
CLAHE
↓
realce local
↓
bordes recuperados

```

# Detección de Sincronización

La sincronización se basa en medias por cuadrante.

```

Q1 Q2

Q3 Q4

```

Se verifica:

```

Q1 ≈ Q4

Q2 ≈ Q3

Q1 ≠ Q2

```

Lo que permite identificar:

```

xo
ox

```

u

```

ox
xo

```

# Detección Temporal de Pulsos

La detección temporal utiliza:

```

diff = abs(frame_actual - frame_anterior)

```

implementado mediante:

```

cv2.absdiff()

```

Posteriormente:

```

threshold()
OR temporal
acumulación histórica

```

# Memoria Temporal

Se utiliza una ventana deslizante de diferencias.

```

historial =

diff(t0)
diff(t1)
diff(t2)
...

```

La acumulación se realiza mediante:

```

acumulada =
diff1 OR diff2 OR diff3 ...

```

Beneficios:

persistencia visual
robustez temporal
tolerancia a FPS bajos
detección de pulsos breves

# Localización del Transmisor

La localización se realiza sobre la imagen de diferencias acumuladas.

Flujo:

```

diff
↓
close
↓
contornos
↓
contorno mayor
↓
minAreaRect()

```

El uso de:

```

cv2.minAreaRect()

```

permite detectar la pantalla incluso cuando:

faltan esquinas
existen líneas internas
aparecen agujeros
hay ruido significativo

# Obtención del Cuadrilátero

A partir del contorno dominante:

```

rect = cv2.minAreaRect(contorno)

box = cv2.boxPoints(rect)

```

Se obtienen las cuatro esquinas del transmisor.

# Rectificación Geométrica

Se emplea:

```

getPerspectiveTransform()

warpPerspective()

```

para transformar la pantalla a una forma cuadrada normalizada.

Antes:

```

/ /
/____/

```

Después:

```

+-------+
| |
| |
| |
+-------+

```

# Extracción de Bits

La región rectificada se normaliza a:

```

200 × 200

```

Posteriormente se divide en una matriz:

```

8 × 8

```

Cada celda representa un bit.

La intensidad media determina:

```

blanco = 1

negro = 0

```

# Máquina de Estados

El receptor implementa tres estados principales.

# Estado 0

```

ESPERANDO_PRIMER_PULSO

```

Objetivo:

localizar transmisor
capturar geometría

# Estado 1

```

ESPERANDO_3_PULSOS

```

Objetivo:

validar inicio de transmisión

# Estado 2

```

RECIBIENDO

```

Objetivo:

recortar
rectificar
demodular
reconstruir mensaje

# Ventajas

Tolerante a ruido.
Tolerante a desenfoque.
Tolerante a reflejos.
Tolerante a pérdida parcial de bordes.
No requiere marcadores fiduciales.
Funciona con cámaras convencionales.
Compatible con video grabado.
Robusto frente a FPS reducidos.

# Limitaciones

Requiere contraste mínimo entre pantalla y fondo.
Reflejos severos pueden ocultar esquinas.
Pulsos extremadamente rápidos pueden perderse.
Dependencia parcial de la selección de ROI.
Sensible a movimientos bruscos de cámara.

# Trabajo Futuro

Kalman Filter.
Seguimiento automático del transmisor.
Corrección automática de exposición.
Reed-Solomon.
CRC.
Sincronización basada en preámbulos extendidos.
Estimación subpixel de esquinas.
Modulación multinivel.
Soporte 16×16 y 32×32.

# Conclusiones

El sistema desarrollado demuestra la viabilidad de implementar un canal de comunicación óptica visible utilizando exclusivamente técnicas clásicas de procesamiento digital de imágenes.

La combinación de sincronización visual, detección temporal de pulsos, memoria de movimiento, extracción robusta de contornos y rectificación geométrica permite recuperar información digital incluso bajo condiciones de captura no ideales.

La arquitectura obtenida constituye una base sólida para futuras investigaciones en comunicaciones ópticas Screen-to-Camera de bajo costo y alta portabilidad.
