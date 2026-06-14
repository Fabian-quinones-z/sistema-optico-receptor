#test videomp4 
import cv2

video = cv2.VideoCapture(
    "docs/test.mp4"
)

count = 0

while True:

    ret, frame = video.read()

    if not ret:
        break

    count += 1

    cv2.imshow("RX", frame)

    if cv2.waitKey(200) == 27:
        break

print("Frames:", count)

video.release()
cv2.destroyAllWindows()
