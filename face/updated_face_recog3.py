import cv2
import face_recognition

# Path to the image file
image_path = r"C:\Users\iarha\OneDrive\Pictures\GooglePhotos\farewell_amity\7E0A4348.jpg"  # Replace with your image path

# Load the image
image = face_recognition.load_image_file(image_path)
face_locations = face_recognition.face_locations(image)

if not face_locations:
    print("No faces were detected in the image.")
    exit()

# Convert to OpenCV format
image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

# Resize the image for display (scale it down to fit the screen)
scale_factor = 0.5  # Adjust the scale factor as needed
resized_image = cv2.resize(image_bgr, (0, 0), fx=scale_factor, fy=scale_factor)

# Dictionary to store names for each face
face_names = {}
selected_face = None  # Track the currently selected face

# Function to handle mouse click events
def mouse_callback(event, x, y, flags, param):
    global selected_face, face_names
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if the click is inside any face rectangle
        for i, (top, right, bottom, left) in enumerate(face_locations):
            # Resize the face coordinates to match the resized image
            top = int(top * scale_factor)
            right = int(right * scale_factor)
            bottom = int(bottom * scale_factor)
            left = int(left * scale_factor)

            if left <= x <= right and top <= y <= bottom:
                selected_face = i  # Record the selected face index
                print(f"Face {i + 1} selected. Enter name in the terminal.")
                break

# Attach mouse callback to the OpenCV window
cv2.namedWindow("Name the Faces")
cv2.setMouseCallback("Name the Faces", mouse_callback)

while True:
    # Create a copy of the resized image for live display
    temp_image = resized_image.copy()

    # Draw rectangles around all faces
    for i, (top, right, bottom, left) in enumerate(face_locations):
        # Resize the face coordinates to match the resized image
        top = int(top * scale_factor)
        right = int(right * scale_factor)
        bottom = int(bottom * scale_factor)
        left = int(left * scale_factor)

        color = (0, 255, 0) if i != selected_face else (0, 0, 255)  # Highlight selected face
        cv2.rectangle(temp_image, (left, top), (right, bottom), color, 2)
        # Display names if they exist
        if i in face_names:
            label_position = (left, bottom + 20)
            cv2.putText(temp_image, face_names[i], label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Show the image
    cv2.imshow("Name the Faces", temp_image)

    # If a face is selected, prompt for a name
    if selected_face is not None:
        name = input(f"Enter name for Face {selected_face + 1}: ")
        face_names[selected_face] = name
        selected_face = None  # Reset selection after naming

    # Press 'q' to save and exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Annotate the original image (not resized) with names
image_with_names = image_bgr.copy()  # Use the original image for saving
for i, (top, right, bottom, left) in enumerate(face_locations):
    if i in face_names:
        # Resize the face coordinates to match the original image
        label_position = (left, bottom + 20)
        cv2.putText(image_with_names, face_names[i], label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# Save the final annotated image
cv2.imwrite("last_annotated.jpg", image_with_names)
cv2.destroyAllWindows()

print("Final annotated image saved as 'last_annotated.jpg'.")


#click the picture, add the name in terminal; click next; add new name.