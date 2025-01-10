#importing dependencies
import face_recognition #face detection library
import cv2 #openCV for video capture and frame handling
import numpy as np #numerical operations

# webcam initialization
video_capture = cv2.VideoCapture(0)

# loading known face
ishits_image = face_recognition.load_image_file(r"C:\Documents_Ishit\pic1.jpg") #loads knowns face
ishits_face_encoding = face_recognition.face_encodings(ishits_image)[0] #computes encoding

anurags_image = face_recognition.load_image_file(r"C:\Users\iarha\Dropbox\PC\Downloads\anurag.jpg")
anurags_face_encoding = face_recognition.face_encodings(anurags_image)[0]

swatis_image = face_recognition.load_image_file(r"C:\Users\iarha\Dropbox\PC\Downloads\swati.jpg")
swatis_face_encoding = face_recognition.face_encodings(swatis_image)[0]

known_face_encodings = [ #stores face encoding
    ishits_face_encoding,
    anurags_face_encoding,
    swatis_face_encoding
]
known_face_names = [ #corresponding names for comparison
    "Ishit",
    "Anurag",
    "Swati"
]
# variable initialization
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

#main loop
while True:
    ret, frame = video_capture.read()
    #frame skipping for process
    if process_this_frame:
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        # face detection and encoding
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # face matching
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)#check
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2) # box
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED) #label
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # image
    cv2.imshow('Video', frame)
    # 'q'to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ends webcam operation
video_capture.release()
cv2.destroyAllWindows()