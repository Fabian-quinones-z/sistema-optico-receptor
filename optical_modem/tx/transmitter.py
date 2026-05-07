import cv2

from common.utils import text_to_bits
from tx.frame_builder import build_frame

message = "Hola modem optico"

bits = text_to_bits(message)

frame = build_frame(bits)

cv2.imwrite("outputs/frame.png", frame)

print("[OK] Frame generado")
