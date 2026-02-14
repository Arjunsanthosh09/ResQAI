import cv2
from datetime import datetime

cap = cv2.VideoCapture(0)

print("Press 'a' to simulate accident detection.")
print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("RESQAI - Live Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('a'):
        print("🚨 Accident Detected!")
        print("Time:", datetime.now())

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()