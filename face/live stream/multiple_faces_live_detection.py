#import dependencies
import cv2
import face_recognition
# uploada photos and assigned names
ishit_image = face_recognition.load_image_file(r"C:\Documents_Ishit\pic1.jpg")
ishit_face_encoding = face_recognition.face_encodings(ishit_image)[0]

person2_image = face_recognition.load_image_file(r"C:\Users\iarha\Dropbox\PC\Downloads\anurag.jpg")
anurag_face_encoding = face_recognition.face_encodings(person2_image)[0]

person3_image = face_recognition.load_image_file(r"C:\Users\iarha\Dropbox\PC\Downloads\swati.jpg")
swati_face_encoding = face_recognition.face_encodings(person3_image)[0]

# store encodings and names
known_face_encodings = [
    ishit_face_encoding,
    anurag_face_encoding,
    swati_face_encoding
]
known_face_names = [
    "Ishit",
    "Anurag",
    "Swati"
]
# Initialize the webcam
video_capture = cv2.VideoCapture(0)  # 0 for default webcam

while True:
    ret, frame = video_capture.read() # frame capture
    # Find all faces and their encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown Person"  # if no result found.
        # assigning the name on matching
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        # rectangle,label
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    # Display
    cv2.imshow("Video", frame)
    # quits by pressing q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# Release the webcam and close all OpenCV windows
video_capture.release()
cv2.destroyAllWindows()
