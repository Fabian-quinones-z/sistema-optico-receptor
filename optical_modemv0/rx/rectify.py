import cv2


def rectify_frame(img, angulo):

    h,w = img.shape[:2]

    M = cv2.getRotationMatrix2D(
        (w/2,h/2),
        angulo,
        1.0
    )

    return cv2.warpAffine(
        img,
        M,
        (w,h)
    )
