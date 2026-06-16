import cv2

_frame_anterior = None


def detectar_cambio(
    frame,
    maxScore=0
):

    global _frame_anterior

    if _frame_anterior is None:

        _frame_anterior = frame.copy()

        return 0,0,None

    diff = cv2.absdiff(
        frame,
        _frame_anterior
    )

    score = int(
        diff.sum() / 255
    )

    if score > maxScore:
        maxScore = score

    _frame_anterior = frame.copy()

    return score,maxScore,diff
