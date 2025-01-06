import face_recognition
import cv2

# Load the image
image_path = "C:\\Documents_Ishit\\pic1.jpg"  # Update with the correct path
try:
    image = face_recognition.load_image_file(image_path)
except FileNotFoundError:
    print(f"Error: The image file at '{image_path}' was not found.")
    exit(1)

# Detect face locations
face_locations = face_recognition.face_locations(image)

# Check if any faces are detected
if not face_locations:  # if `face_locations` is empty
    print("No faces were detected in the image.")
else:
    print(f"Detected {len(face_locations)} face(s) in the image.")

    # Convert the image to a format OpenCV can work with (BGR instead of RGB)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Draw a rectangle around each detected face and add a label
    for i, face_location in enumerate(face_locations):
        top, right, bottom, left = face_location
        print(f"Face {i + 1}: Top={top}, Right={right}, Bottom={bottom}, Left={left}")

        # Draw a rectangle around the face
        cv2.rectangle(image_bgr, (left, top), (right, bottom), (0, 255, 0), 2)

        # Add a label (e.g., a name) below the rectangle
        label = f"Face {i + 1} : Ishit"  # Customize text here (e.g., use a real name if available)
        label_position = (left, bottom + 20)  # Position the text slightly below the rectangle
        cv2.putText(image_bgr, label, label_position,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,100), 4, cv2.LINE_AA)

    # Resize the image for display (scale it down to 50% of its size for smaller window)
    resized_image = cv2.resize(image_bgr, (0, 0), fx=0.5, fy=0.5)  # Adjust scaling as needed

    # Display the resized image in a window
    cv2.imshow("Detected Face(s)", resized_image)

    # Wait for the user to close the window (press any key)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
