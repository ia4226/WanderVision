#dependencies
import face_recognition
import cv2
import os
import numpy as np
#save directory
save_path = r"C:\Users\iarha\PyC proj\.3venv\saved_photos"
if not os.path.exists(save_path):
    os.makedirs(save_path)
#load known faces from directory
def load_known_faces(directory):
    known_encodings = []
    known_names = []
    for file in os.listdir(directory):
        if file.endswith(('.jpg', '.jpeg', '.png')):  # validity of formats
            image_path = os.path.join(directory, file)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:  # If a face is detected
                known_encodings.append(encodings[0])
                name = os.path.splitext(file)[0]
                known_names.append(name)
    return known_encodings, known_names
# ;oad known faces initially
known_face_encodings, known_face_names = load_known_faces(save_path)
# open webcam
video_capture = cv2.VideoCapture(0)
# realtime processing variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
print("Press 'c' to capture a photo and 'q' to quit.")
# Main loop
while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Error: Could not read frame from webcam!")
        break

    #frame skipping for process efficiency
    if process_this_frame:
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        #face detection and encoding
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        #face matching
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame
    # annotate results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)  # Draw box
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)  # Label box
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    #show video
    cv2.imshow('Video', frame)
    # Key press handling
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):  # Capture
        if face_names:
            for name in face_names:
                if name == "Unknown":
                    # Ask for a name if unknown
                    name = input("Enter a name for the unknown person: ").strip()
                # Save the image
                existing_files = [f for f in os.listdir(save_path) if f.startswith(name)]
                file_name = f"{name}_{len(existing_files) + 1}.jpg"
                save_file = os.path.join(save_path, file_name)
                cv2.imwrite(save_file, frame)
                print(f"Saved: {save_file}")
                # Add new face encoding
                new_image = face_recognition.load_image_file(save_file)
                new_encoding = face_recognition.face_encodings(new_image)
                if new_encoding:
                    known_face_encodings.append(new_encoding[0])
                    known_face_names.append(name)
        else:
            print("No face detected. Cannot capture.")

    elif key == ord('q'):  # Quit
        break
#end operations
video_capture.release()
cv2.destroyAllWindows()
