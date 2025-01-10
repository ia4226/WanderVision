#import dependencies
import cv2
import os
#capture, save images
def capture_and_save_images(save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    #webcam initialized
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print("Press 'c' to capture a photo and 'q' to quit.")
#real time feed and face detection
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break
        #grayscale conversion
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        #rectangles around the face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        #displaying the video feed
        cv2.imshow('Video Feed', frame)

        # c <- capture, s <- save.
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):  # Capture photo
            name = input("Enter the name of the person: ")
            #create a unique filename for each photo.
            file_name = f"{name}_{len(os.listdir(save_path)) + 1}.jpg"
            save_file = os.path.join(save_path, file_name)
            cv2.imwrite(save_file, frame)
            print(f"Saved: {save_file}")
        elif key == ord('q'):  # Quit
            break

    cap.release()
    cv2.destroyAllWindows()

# Provide the folder path where photos will be saved
folder_path = r"C:\Users\iarha\PyC proj\.3venv\saved_photos"
capture_and_save_images(folder_path)
