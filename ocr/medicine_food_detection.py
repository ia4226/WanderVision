import cv2
import easyocr
import numpy as np
import time  # Used for elapsed time calculations

# Use EasyOCR on the CPU (forcing this since GPU is unavailable)
reader = easyocr.Reader(['en'], gpu=False)

# Access the webcam
cap = cv2.VideoCapture(0)

# Exit if the webcam could not be accessed
if not cap.isOpened():
    print("Error: Could not access the webcam.")
    exit()

# Set the video frame resolution (smaller resolution for performance improvement)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# Define a region of interest (ROI) if text is expected only in a specific area
def get_roi(frame):
    height, width = frame.shape[:2]
    x_start, y_start = int(width * 0.1), int(height * 0.4)  # Adjust ROI coordinates
    x_end, y_end = int(width * 0.9), int(height * 0.9)
    return frame[y_start:y_end, x_start:x_end]


# Frame counter and OCR sampling frequency
frame_count = 0
ocr_frequency = 60  # Perform OCR every 60th frame

# Variables to track detection and time
detected_danger = False
detected_medicine = False
danger_timeout = 7  # Duration to keep danger warning visible (in seconds)
medicine_timeout = 7  # Duration to keep medicine notes visible (in seconds)

last_danger_time = 0  # Stores the last time "Sugar" was detected
last_medicine_time = 0  # Stores the last time "Paracetamol" was detected

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Pre-process the image using thresholding for easier text detection
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Apply ROI selection to zoom in on relevant areas of text
    roi = get_roi(processed)

    # Perform OCR only on every `ocr_frequency` frame
    if frame_count % ocr_frequency == 0:
        # Run OCR on the ROI
        ocr_results = reader.readtext(roi)
        for result in ocr_results:
            bbox, word, confidence = result
            if confidence > 0.4:  # Lowered confidence threshold
                (x1, y1), (x2, y2) = bbox[0], bbox[2]
                # Translate bounding box coordinates to the full frame
                h, w = gray.shape[:2]
                x_start, y_start = int(w * 0.1), int(h * 0.4)
                x1, y1, x2, y2 = x1 + x_start, y1 + y_start, x2 + x_start, y2 + y_start

                # Draw bounding boxes and recognized text on the original frame
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(frame, word, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

                # Check if the detected word matches either "Sugar" or "Paracetamol"
                if "sugar" in word.lower():
                    detected_danger = True
                    last_danger_time = time.time()  # Record the current time
                elif "paracetamol" in word.lower():
                    detected_medicine = True
                    last_medicine_time = time.time()  # Record the current time

    # Check if the danger warning should still be visible
    if detected_danger and (time.time() - last_danger_time < danger_timeout):
        # Display the danger alert
        cv2.putText(
            frame,
            "DANGER: Sugar Detected!",
            (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3
        )
    else:
        detected_danger = False

    # Check if the medicine note should still be visible
    if detected_medicine and (time.time() - last_medicine_time < medicine_timeout):
        # Display the note for "Paracetamol"
        cv2.putText(
            frame,
            "Reminder: Take Paracetamol at 6:00pm",
            (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3
        )
    else:
        detected_medicine = False

    # Display the processed live feed
    cv2.imshow('OCR - Press q to quit', frame)

    # Exit if the "q" key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Increment the frame count
    frame_count += 1

# Release the video capture and destroy OpenCV windows
cap.release()
cv2.destroyAllWindows()
