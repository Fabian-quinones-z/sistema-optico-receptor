import cv2
import numpy as np

img = np.zeros((400,400), dtype=np.uint8)

cv2.putText(
    img,
    "TEST",
    (80,200),
    cv2.FONT_HERSHEY_SIMPLEX,
    2,
    255,
    3
)

cv2.imshow("test", img)

cv2.waitKey(0)

cv2.destroyAllWindows()
