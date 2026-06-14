import os
import cv2

from common.utils import text_to_bits
from common.config import BITS_PER_FRAME
from tx.frame_builder import build_frame
from tx.display import transmit_frames
from tx.control_frames import sync_a, sync_b


message = """
Hola modem optico
"""

bits = text_to_bits(message)

os.makedirs("outputs", exist_ok=True)

total_frames = (
    len(bits) + BITS_PER_FRAME - 1
) // BITS_PER_FRAME

frames = []

# PREÁMBULO
frames.extend([
    sync_a(),
    sync_b(),
    sync_a(),
    sync_b()
])

# DATOS
for i in range(total_frames):

    start = i * BITS_PER_FRAME
    end = start + BITS_PER_FRAME

    frame_bits = bits[start:end]

    frame = build_frame(frame_bits)

    filename = f"outputs/frame_{i:03d}.png"

    cv2.imwrite(filename, frame)

    frames.append(frame)

    print(f"[OK] {filename}")

# POSTÁMBULO
frames.extend([
    sync_a(),
    sync_b(),
    sync_a(),
    sync_b()
])

print(f"\nFrames datos: {total_frames}")
print(f"Frames totales: {len(frames)}")
print(f"Bits totales: {len(bits)}")

transmit_frames(frames)

