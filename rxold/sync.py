import cv2
import numpy as np

#sync.py 
def detectar_sync(gris):

    h,w = gris.shape

    h2 = h//2
    w2 = w//2

    q1 = np.mean(gris[0:h2,0:w2])
    q2 = np.mean(gris[0:h2,w2:w])

    q3 = np.mean(gris[h2:h,0:w2])
    q4 = np.mean(gris[h2:h,w2:w])

    #print(
    #    f"Q={int(q1)},{int(q2)},{int(q3)},{int(q4)}"
    #)

    d1 = abs(q1-q4)
    d2 = abs(q2-q3)

    c1 = abs(q1-q2)
    c2 = abs(q1-q3)

    if d1 < 25 and d2 < 25:
        if c1 > 30 and c2 > 30:
            return "SYNC"

    return "DATA"
