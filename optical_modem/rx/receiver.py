from rx.demodulation import demodulate_image
from common.utils import bits_to_text

bits = demodulate_image("outputs/frame.png")

text = bits_to_text(bits)

print("[RX]")
print(text)
