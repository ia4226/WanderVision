#dependencies
import cv2
import os
#folder/directory to save
directory = r"C:\Users\iarha\PyC proj\.3venv\capture"
if not os.path.exists(directory):
    os.makedirs(directory)  #create if it doesn't exist
#open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not access the webcam!")
    exit()
#read frame
ret, frame = cap.read()
if not ret:
    print("Error: Could not read frame from webcam!")
    cap.release()
    exit()
#display the image
cv2.imshow("Captured Image :) ", frame)
cv2.waitKey(5000)  #display for 5 second, adjustable.
cv2.destroyAllWindows()
#user defined name for the image taken
name = input("Enter the name for the image (without extension): ").strip()
if not name:
    print("Error: Name cannot be empty!")
    cap.release()
    exit()
#iuttput filename
output_filename = f"{name}.jpg"
output_path = os.path.join(directory, output_filename)
try:
    cv2.imwrite(output_path, frame)
    print(f"Image successfully saved as: {output_filename} in {directory}")
except Exception as e:
    print(f"Error saving image: {e}")
#webcam released.
cap.release()
