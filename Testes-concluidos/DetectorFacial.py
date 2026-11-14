
# Importação das bibliotecas
import cv2
import numpy as np
import os
import re


# Choose the face detector
# -> Options: ssd | haarcascade
detector = "haarcascade"

max_width = 800
max_samples = 10
starting_sample_number = 0


# DroidCam configuration
camera_index = 0


# Function to parse the name of the person
def parse_name(name):
    name = re.sub(r"[^\w\s]", '', name)
    name = re.sub(r"\s+", '_', name)
    return name


# Create the final folder where the photos will be saved
def create_folders(final_path, final_path_full):

    if not os.path.exists(final_path):
        os.makedirs(final_path)

    if not os.path.exists(final_path_full):
        os.makedirs(final_path_full)


# Return the detected face using Haar cascades
def detect_face(face_detector, orig_frame):

    frame = orig_frame.copy()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5
    )

    face_roi = None

    for (x, y, w, h) in faces:

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 255),
            2
        )

        face_roi = orig_frame[y:y + h, x:x + w]

        if face_roi.size > 0:
            face_roi = cv2.resize(face_roi, (140, 140))

    return face_roi, frame


# Return the detected face using SSD
def detect_face_ssd(network, orig_frame, show_conf=True, conf_min=0.7):

    frame = orig_frame.copy()

    (h, w) = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)),
        1.0,
        (300, 300),
        (104.0, 117.0, 123.0)
    )

    network.setInput(blob)

    detections = network.forward()

    face_roi = None

    for i in range(0, detections.shape[2]):

        confidence = detections[0, 0, i, 2]

        if confidence > conf_min:

            bbox = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

            (start_x, start_y, end_x, end_y) = bbox.astype("int")

            if (
                start_x < 0 or
                start_y < 0 or
                end_x > w or
                end_y > h
            ):
                continue

            face_roi = orig_frame[start_y:end_y, start_x:end_x]

            if face_roi.size == 0:
                continue

            face_roi = cv2.resize(face_roi, (90, 120))

            cv2.rectangle(
                frame,
                (start_x, start_y),
                (end_x, end_y),
                (0, 255, 0),
                2
            )

            if show_conf:

                text_conf = "{:.2f}%".format(confidence * 100)

                cv2.putText(
                    frame,
                    text_conf,
                    (start_x, start_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

    return face_roi, frame


# Load the face detector
if detector == "ssd":

    network = cv2.dnn.readNetFromCaffe(
        "deploy.prototxt.txt",
        "res10_300x300_ssd_iter_140000.caffemodel"
    )

else:

    # Load Haar Cascade from OpenCV installation
    cascade_path = (
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    face_detector = cv2.CascadeClassifier(cascade_path)

    if face_detector.empty():

        print("Error: Could not load Haar Cascade classifier.")
        exit()


# Video capture object - DroidCam
print("Connecting to DroidCam...")

cam = cv2.VideoCapture(camera_index, cv2.CAP_ANY)

if not cam.isOpened():

    print("Error: Could not connect to DroidCam.")
    print("Check if DroidCam Client is open and connected.")

    cam.release()
    exit()

print("DroidCam connected successfully!")


# Configure camera resolution
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# Folders where the photos will be stored
folder_faces = "dataset/"
folder_full = "dataset_full/"


# The user needs to type their RA
person_name = input("Digite o seu RA: ")

person_name = parse_name(person_name)

if not person_name:

    print("Invalid RA.")

    cam.release()
    exit()


# Join the path (dataset directory + subdirectory)
final_path = os.path.join(folder_faces, person_name)

final_path_full = os.path.join(folder_full, person_name)

print("All photos are going to be saved in {}".format(final_path))


# Create folders
create_folders(final_path, final_path_full)


sample = 0


# Loop over every frame of the video stream
while True:

    ret, frame = cam.read()

    # Check if the camera is sending images
    if not ret or frame is None:

        print("Error receiving image from DroidCam.")
        break

    # Resize only if a max_width is specified
    if max_width is not None:

        video_width = max_width

        video_height = int(
            frame.shape[0] * (max_width / frame.shape[1])
        )

        frame = cv2.resize(
            frame,
            (video_width, video_height)
        )

    # Detect faces
    if detector == "ssd":

        face_roi, processed_frame = detect_face_ssd(
            network,
            frame
        )

    else:

        face_roi, processed_frame = detect_face(
            face_detector,
            frame
        )

    # Display capture instructions
    if face_roi is not None:

        cv2.putText(
            processed_frame,
            "Press Q to capture",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            processed_frame,
            "No face detected",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    # Show the camera image
    cv2.imshow("Capturing face", processed_frame)

    # Read keyboard input only once per frame
    key = cv2.waitKey(1) & 0xFF

    # Press Q to capture the detected face
    if key == ord('q'):

        if face_roi is not None:

            sample += 1

            photo_sample = (
                sample + starting_sample_number - 1
                if starting_sample_number > 0
                else sample
            )

            image_name = (
                person_name + "." +
                str(photo_sample) + ".jpg"
            )

            # Save the cropped face
            cv2.imwrite(
                os.path.join(final_path, image_name),
                face_roi
            )

            # Save the full image
            cv2.imwrite(
                os.path.join(final_path_full, image_name),
                frame
            )

            print("=> photo " + str(sample))

            cv2.imshow("face", face_roi)

        else:

            print("No face detected. Try again.")

    # Press ESC to exit the program
    if key == 27:
        print("Capture interrupted.")
        break

    # Finish when the maximum number of photos is reached
    if sample >= max_samples:
        break


# Finish the capture
print("Completed!")

cam.release()

cv2.destroyAllWindows()
