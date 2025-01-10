#dependencies
import cv2
import os
# directory
directory = r"C:\Users\iarha\PyC proj\.3venv\capture"
if not os.path.exists(directory):
    os.makedirs(directory)  # Create
#webcam opens
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not access the webcam!")
    exit()
#frame
ret, frame = cap.read()
if not ret:
    print("Error: Could not read frame from webcam!")
    cap.release()
    exit()
#display
cv2.imshow("Captured Image :)", frame)
cv2.waitKey(5000)  # Display for 5 seconds, adjustable
cv2.destroyAllWindows()
#name the output file
output_filename = "captured_image.jpg"
output_path = os.path.join(directory, output_filename)
try:
    cv2.imwrite(output_path, frame)
    print(f"Image successfully saved at: {output_path}")
except Exception as e:
    print(f"Error saving image: {e} !")
#webcam released
cap.release()
