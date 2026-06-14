import cv2

def transmit_frames(frames, duration=300):

    cv2.namedWindow(
        "TX",
        cv2.WINDOW_NORMAL
    )

    cv2.setWindowProperty(
        "TX",
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    for frame in frames:
        #print("mostrando frame")

        cv2.imshow("TX", frame)

        key = cv2.waitKey(duration)

        if key == 27:
            break

    cv2.destroyAllWindows()
