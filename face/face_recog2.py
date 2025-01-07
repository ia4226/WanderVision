import face_recognition
import cv2

# List of image file paths and corresponding names
image_files = [
    {"path": r"C:\Users\iarha\Dropbox\PC\Downloads\sports_photos\sania.jpeg", "name": "sania"},  # Replace with actual paths and names
    {"path": r"C:\Users\iarha\Dropbox\PC\Downloads\sports_photos\saina.jpeg", "name": "saina"},
    {"path": r"C:\Users\iarha\Dropbox\PC\Downloads\sports_photos\sindhu.jpeg", "name": "sindhu"},
    {"path": r"C:\Users\iarha\Dropbox\PC\Downloads\sports_photos\sunil.jpeg", "name": "sunil"},
    {"path": r"C:\Users\iarha\Dropbox\PC\Downloads\sports_photos\neeraj.jpeg", "name": "neeraj"}
]

# Process each image
for entry in image_files:
    image_path = entry["path"]
    name = entry["name"]

    print(f"\nProcessing image: {image_path} (Name: {name})")
    try:
        # Load the image
        image = face_recognition.load_image_file(image_path)
    except FileNotFoundError:
        print(f"Error: The image file '{image_path}' was not found.")
        continue

    # Detect face locations
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        print("No faces detected in the image.")
    else:
        print(f"Detected {len(face_locations)} face(s) in the image.")

        # Convert image to OpenCV's BGR format
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw rectangles and names for each detected face
        for i, face_location in enumerate(face_locations):
            top, right, bottom, left = face_location
            print(f"Face {i + 1}: Top={top}, Right={right}, Bottom={bottom}, Left={left}")

            # Draw a rectangle around the face
            cv2.rectangle(image_bgr, (left, top), (right, bottom), (0, 255, 0), 2)

            # Add a label (name) below the rectangle
            label_position = (left, bottom + 20)
            cv2.putText(image_bgr, name, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Resize the image for better visibility (optional)
        resized_image = cv2.resize(image_bgr, (0, 0), fx=0.5, fy=0.5)

        # Display the image
        cv2.imshow(f"Faces in {image_path}", resized_image)

        # Wait for a key press to proceed to the next image
        cv2.waitKey(0)
        cv2.destroyAllWindows()
