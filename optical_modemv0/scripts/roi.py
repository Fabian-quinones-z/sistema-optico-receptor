import cv2


def select_roi(frame):

    roi = cv2.selectROI(
        "Seleccionar pantalla",
        frame,
        False
    )

    cv2.destroyWindow(
        "Seleccionar pantalla"
    )

    return roi 
