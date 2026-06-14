# Optical Modem

Sistema de comunicación óptica pantalla-cámara (Screen-to-Camera Optical Communication).

El transmisor genera tramas binarias visuales mostradas en pantalla y el receptor recupera la información desde una cámara o un video previamente grabado.

---

# Estado actual

Implementado:

* Generación de tramas 8x8.
* 8 bytes (64 bits) por frame.
* Generación automática de múltiples frames.
* Preámbulo y postámbulo de sincronización.
* Reproducción de frames por pantalla.
* Captura desde cámara o video.
* Selección de ROI.
* Conversión a escala de grises.
* Binarización fija u OTSU.
* Detección de sincronización.
* Detección de movimiento temporal.
* Detección de líneas mediante Hough.
* Estimación de ángulo dominante.
* Rectificación geométrica.

Pendiente:

* Demodulación completa 8x8.
* Reconstrucción de mensajes.
* Corrección de errores.
* Sincronización automática de frames.
* Seguimiento dinámico de ROI.

---

# Estructura

```text
optical_modem/

├── common/
│   ├── coding.py
│   ├── config.py
│   └── utils.py
│
├── tx/
│   ├── transmitter.py
│   ├── frame_builder.py
│   ├── display.py
│   ├── control_frames.py
│   ├── modulation.py
│   └── protocol.py
│
├── rx/
│   ├── receiver.py
│   ├── sync.py
│   ├── motion.py
│   ├── geometry.py
│   ├── rectify.py
│   ├── demodulation.py
│   └── config_rx.py
│
├── scripts/
│   ├── roi.py
│   ├── detectar_pantalla.py
│   ├── rectificar.py
│   └── firma_horizontal.py
│
├── tests/
│
├── docs/
│   └── muestra.mp4
│
├── outputs/
│
└── run.py
```

---

# Protocolo de transmisión

Cada frame contiene:

```text
8 x 8 = 64 bits
```

equivalente a:

```text
8 bytes por frame
```

---

# Sincronización

Se utilizan dos patrones alternados.

SYNC_A

```text
xo
ox
```

SYNC_B

```text
ox
xo
```

donde:

```text
o = bloque blanco
x = bloque negro
```

Cada bloque ocupa:

```text
4x4 bits
```

por lo que el patrón completo ocupa:

```text
8x8 bits
```

igual que un frame de datos.

---

# Estructura de transmisión

```text
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

---

# Pipeline del transmisor

```text
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

---

# Pipeline del receptor

```text
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

---

# Detección de sincronización

El receptor calcula medias por cuadrante:

```text
Q1 Q2

Q3 Q4
```

y verifica:

```text
Q1 ≈ Q4

Q2 ≈ Q3

Q1 ≠ Q2
```

para identificar:

```text
xo
ox
```

u

```text
ox
xo
```

---

# Detección temporal

El módulo:

```text
rx/motion.py
```

realiza:

```text
frame_actual - frame_anterior
```

mediante:

```python
cv2.absdiff()
```

para detectar la alternancia:

```text
SYNC_A ↔ SYNC_B
```

que produce grandes cambios temporales.

---

# Instalación

Crear entorno virtual:

```bash
python3 -m venv venv
```

Activar:

```bash
source venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

# Ejecución rápida

Menú principal:

```bash
venv/bin/python3 run.py
```

---

# Transmisor

```bash
venv/bin/python3 -m tx.transmitter
```

---

# Receptor

```bash
venv/bin/python3 -m rx.receiver
```

---

# Fuente de video

Modificar:

```python
rx/config_rx.py
```

Para usar cámara:

```python
USE_CAMERA = True
```

Para usar archivo:

```python
USE_CAMERA = False
VIDEO_FILE = "docs/muestra.mp4"
```

---

# Archivos generados

Frames de datos:

```text
outputs/frame_000.png
outputs/frame_001.png
outputs/frame_002.png
...
```

---

# Próximo objetivo

Implementar:

```text
rectificación automática
+
muestreo 8x8
+
demodulación binaria
+
reconstrucción ASCII
```

para recuperar completamente el mensaje transmitido.
