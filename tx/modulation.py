import numpy as np

def ook_modulate(bits):
    return np.array([255 if b == '1' else 0 for b in bits],
                    dtype=np.uint8)
import numpy as np

def ook_modulate(bits):
    return np.array([255 if b == '1' else 0 for b in bits],
                    dtype=np.uint8)
