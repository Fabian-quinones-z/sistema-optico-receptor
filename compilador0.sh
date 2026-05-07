#!/bin/bash
set -euo pipefail

echo "=== Creando proyecto optical_modem ==="

PROJECT="optical_modem"

# =========================================================
# ESTRUCTURA BASE
# =========================================================

mkdir -p $PROJECT/{tx,rx,common,tests,samples,outputs,docs,scripts}

cd $PROJECT

touch README.md
touch requirements.txt
touch .gitignore

# =========================================================
# ENTORNO VIRTUAL
# =========================================================

python3 -m venv venv

# =========================================================
# GITIGNORE
# =========================================================

cat >> .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
*.pyo
*.png
*.jpg
*.mp4
outputs/
.idea/
.vscode/
EOF

# =========================================================
# REQUIREMENTS
# =========================================================

cat >> requirements.txt << 'EOF'
numpy
scipy
opencv-python
matplotlib
reedsolo
tqdm
scikit-image
EOF

# =========================================================
# COMMON
# =========================================================

touch common/__init__.py
touch common/utils.py
touch common/config.py
touch common/coding.py

cat >> common/config.py << 'EOF'
FRAME_SIZE = 800

GRID_ROWS = 64
GRID_COLS = 64

CELL_SIZE = 10

SYMBOL_TIME_MS = 150

THRESHOLD = 127
EOF

cat >> common/utils.py << 'EOF'
def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bits_to_text(bits):
    chars = []

    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]

        if len(byte) < 8:
            continue

        chars.append(chr(int(byte, 2)))

    return ''.join(chars)
EOF

cat >> common/coding.py << 'EOF'
from reedsolo import RSCodec

RSC = RSCodec(10)

def encode_rs(data: bytes):
    return RSC.encode(data)

def decode_rs(data: bytes):
    return RSC.decode(data)
EOF

# =========================================================
# TX
# =========================================================

touch tx/__init__.py
touch tx/transmitter.py
touch tx/frame_builder.py
touch tx/modulation.py
touch tx/protocol.py

cat >> tx/modulation.py << 'EOF'
import numpy as np

def ook_modulate(bits):
    return np.array([255 if b == '1' else 0 for b in bits],
                    dtype=np.uint8)
EOF

cat >> tx/frame_builder.py << 'EOF'
import cv2
import numpy as np

from common.config import *

def build_frame(bits):

    frame = np.zeros(
        (FRAME_SIZE, FRAME_SIZE),
        dtype=np.uint8
    )

    idx = 0

    for r in range(GRID_ROWS):

        for c in range(GRID_COLS):

            if idx >= len(bits):
                break

            y1 = r * CELL_SIZE
            y2 = y1 + CELL_SIZE

            x1 = c * CELL_SIZE
            x2 = x1 + CELL_SIZE

            color = 255 if bits[idx] == '1' else 0

            frame[y1:y2, x1:x2] = color

            idx += 1

    return frame
EOF

cat >> tx/transmitter.py << 'EOF'
import cv2

from common.utils import text_to_bits
from tx.frame_builder import build_frame

message = "Hola modem optico"

bits = text_to_bits(message)

frame = build_frame(bits)

cv2.imwrite("outputs/frame.png", frame)

print("[OK] Frame generado")
EOF

# =========================================================
# RX
# =========================================================

touch rx/__init__.py
touch rx/receiver.py
touch rx/detect_screen.py
touch rx/rectify.py
touch rx/demodulation.py
touch rx/sync.py

cat >> rx/demodulation.py << 'EOF'
import cv2

from common.config import *

def demodulate_image(path):

    img = cv2.imread(path, 0)

    bits = ""

    for r in range(GRID_ROWS):

        for c in range(GRID_COLS):

            y = r * CELL_SIZE + CELL_SIZE // 2
            x = c * CELL_SIZE + CELL_SIZE // 2

            pixel = img[y, x]

            bits += '1' if pixel > THRESHOLD else '0'

    return bits
EOF

cat >> rx/receiver.py << 'EOF'
from rx.demodulation import demodulate_image
from common.utils import bits_to_text

bits = demodulate_image("outputs/frame.png")

text = bits_to_text(bits)

print("[RX]")
print(text)
EOF

# =========================================================
# TESTS
# =========================================================

touch tests/static_image_test.py
touch tests/video_test.py
touch tests/realtime_test.py

cat >> tests/static_image_test.py << 'EOF'
print("TODO: static image test")
EOF

# =========================================================
# README
# =========================================================

cat >> README.md << 'EOF'
# Optical Modem

Sistema de comunicación óptica pantalla-cámara.

## Estructura

- tx/: transmisor
- rx/: receptor
- common/: utilidades compartidas
- tests/: pruebas

## Setup

source venv/bin/activate

pip install -r requirements.txt

## Ejecutar TX

python tx/transmitter.py

## Ejecutar RX

python rx/receiver.py
EOF

# =========================================================
# SCRIPT DE INSTALACION
# =========================================================

cat >> scripts/setup.sh << 'EOF'
#!/bin/bash
set -euo pipefail

source venv/bin/activate

pip install -r requirements.txt
EOF

chmod +x scripts/setup.sh

# =========================================================
# FINAL
# =========================================================

echo ""
echo "======================================="
echo "Proyecto creado correctamente"
echo "======================================="
echo ""
echo "Siguientes pasos:"
echo ""
echo "cd $PROJECT"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo ""
echo "TX:"
echo "python tx/transmitter.py"
echo ""
echo "RX:"
echo "python rx/receiver.py"
echo "" 
