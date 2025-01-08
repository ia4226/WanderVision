import cv2
import face_recognition

# Load your uploaded photo and encode it
your_image = face_recognition.load_image_file(r"C:\Documents_Ishit\pic1.jpg")
your_face_encoding = face_recognition.face_encodings(your_image)[0]

# Initialize the webcam
video_capture = cv2.VideoCapture(0)  # 0 for default webcam

while True:
    # Capture each frame of the video
    ret, frame = video_capture.read()

    # Find all faces and their encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare the face in the frame with your uploaded photo
        matches = face_recognition.compare_faces([your_face_encoding], face_encoding)

        if True in matches:
            name = "It's you, Ishit!"
        else:
            name = "Unknown Person"

        # Draw a box around the face and label it
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Display the resulting frame
    cv2.imshow("Video", frame)

    # Exit the video loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
video_capture.release()
cv2.destroyAllWindows()
