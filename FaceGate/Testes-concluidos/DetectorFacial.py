
# ==========================================
# IMPORTAÇÃO DAS BIBLIOTECAS
# ==========================================

import cv2
import numpy as np
import os
import re
import time


# ==========================================
# CONFIGURAÇÕES DO DETECTOR
# ==========================================

# Options: ssd | haarcascade

#detector = "haarcascade"
detector = "ssd"

max_width = 800
max_samples = 10
starting_sample_number = 0


# ==========================================
# CONFIGURAÇÃO DROIDCAM
# ==========================================

camera_index = 0


# ==========================================
# FUNÇÃO PARA TRATAR O RA
# ==========================================

def parse_name(name):

    name = re.sub(r"[^\w\s]", '', name)
    name = re.sub(r"\s+", '_', name)

    return name


# ==========================================
# CRIAÇÃO DAS PASTAS
# ==========================================

def create_folders(final_path, final_path_full):

    os.makedirs(final_path, exist_ok=True)
    os.makedirs(final_path_full, exist_ok=True)


# ==========================================
# DETECTOR FACIAL - HAAR CASCADE
# ==========================================

def detect_face(face_detector, orig_frame):

    frame = orig_frame.copy()

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

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

            face_roi = cv2.resize(
                face_roi,
                (140, 140)
            )

    return face_roi, frame


# ==========================================
# DETECTOR FACIAL - SSD
# ==========================================

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

            bbox = (
                detections[0, 0, i, 3:7] *
                np.array([w, h, w, h])
            )

            (start_x, start_y, end_x, end_y) = bbox.astype("int")

            if (
                start_x < 0 or
                start_y < 0 or
                end_x > w or
                end_y > h or
                end_x <= start_x or
                end_y <= start_y
            ):
                continue

            face_roi = orig_frame[
                start_y:end_y,
                start_x:end_x
            ]

            if face_roi.size == 0:
                continue

            face_roi = cv2.resize(
                face_roi,
                (90, 120)
            )

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


# ==========================================
# CARREGAMENTO DO DETECTOR FACIAL
# ==========================================

base_dir = os.path.dirname(os.path.abspath(__file__))


if detector == "ssd":

    network = cv2.dnn.readNetFromCaffe(

        os.path.join(
            base_dir,
            "..",
            "Modelos",
            "deploy.prototxt.txt"
        ),

        os.path.join(
            base_dir,
            "..",
            "Modelos",
            "res10_300x300_ssd_iter_140000.caffemodel"
        )

    )

else:

    cascade_path = os.path.join(
        base_dir,
        "..",
        "Modelos",
        "haarcascade_frontalface_default.xml"
    )

    cascade_path = os.path.abspath(cascade_path)

    face_detector = cv2.CascadeClassifier(cascade_path)

    if face_detector.empty():

        print("Error: Could not load Haar Cascade classifier.")
        print("File location:", cascade_path)

        exit()

    print("Haar Cascade loaded successfully!")


# ==========================================
# CONEXÃO COM DROIDCAM
# ==========================================

print("Procurando uma câmera disponível...")

def encontrar_camera():
    for indice in range(3):
        print(f"Testando câmera no índice {indice}...")

        cam = cv2.VideoCapture(indice, cv2.CAP_ANY)

        if cam.isOpened():
            ret, frame = cam.read()

            if ret and frame is not None:
                print(f"Câmera encontrada no índice {indice}!")
                return cam

        cam.release()

    return None

cam = encontrar_camera()

if cam is None:
    print("Erro: nenhuma câmera funcional foi encontrada.")
    exit()

print("Câmera conectada com sucesso!")

time.sleep(2)


# ==========================================
# CONFIGURAÇÃO DA RESOLUÇÃO
# ==========================================

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# ==========================================
# PASTAS DE ARMAZENAMENTO
# ==========================================

folder_faces = os.path.join(
    base_dir,
    "dataset"
)

folder_full = os.path.join(
    base_dir,
    "dataset_full"
)


# ==========================================
# IDENTIFICAÇÃO DO USUÁRIO
# ==========================================

person_name = input("Digite o seu RA: ")

person_name = parse_name(person_name)

if not person_name:

    print("Invalid RA.")

    cam.release()
    exit()


# ==========================================
# CAMINHOS DAS FOTOGRAFIAS
# ==========================================

final_path = os.path.join(
    folder_faces,
    person_name
)

final_path_full = os.path.join(
    folder_full,
    person_name
)

print("Rostos serão salvos em:", final_path)
print("Imagens completas serão salvas em:", final_path_full)


# ==========================================
# CRIAÇÃO DAS PASTAS DO USUÁRIO
# ==========================================

create_folders(
    final_path,
    final_path_full
)


# ==========================================
# CONTADOR DE FOTOGRAFIAS
# ==========================================

sample = 0


# ==========================================
# CAPTURA E PROCESSAMENTO DAS IMAGENS
# ==========================================

while True:

    ret, frame = cam.read()

    if not ret or frame is None:

        print("Error receiving image from DroidCam.")
        break

    # Redimensionamento da imagem

    if max_width is not None:

        video_width = max_width

        video_height = int(
            frame.shape[0] *
            (max_width / frame.shape[1])
        )

        frame = cv2.resize(
            frame,
            (video_width, video_height)
        )

    # Detecção facial

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

    # ======================================
    # CONVERSÃO DA VISUALIZAÇÃO PARA CINZA
    # ======================================

    display_frame = cv2.cvtColor(
        processed_frame,
        cv2.COLOR_BGR2GRAY
    )

    # Instruções na tela

    if face_roi is not None:

        cv2.putText(
            display_frame,
            "Press Q to capture",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            255,
            2
        )

    else:

        cv2.putText(
            display_frame,
            "No face detected",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            255,
            2
        )

    # Mostrar câmera em preto e branco

    # Exibe a câmera em cores
    #cv2.imshow("Capturing face", frame)
    cv2.imshow("Capturing face", processed_frame)

    # Capturar tecla pressionada

    key = cv2.waitKey(10) & 0xFF

    if key != 255:
        print("Tecla detectada:", key)

    # ======================================
    # SALVAR FOTOGRAFIA COM Q
    # ======================================

    if key == ord('q') or key == ord('Q'):

        if face_roi is not None:

            # Converter rosto para preto e branco

            face_roi_bw = cv2.cvtColor(
                face_roi,
                cv2.COLOR_BGR2GRAY
            )

            # Converter imagem completa para preto e branco

            frame_bw = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            # Nome da fotografia

            photo_sample = (
                sample + starting_sample_number + 1
            )

            image_name = (
                person_name + "." +
                str(photo_sample) + ".jpg"
            )

            # Caminhos completos

            face_image_path = os.path.join(
                final_path,
                image_name
            )

            full_image_path = os.path.join(
                final_path_full,
                image_name
            )

            # Salvar rosto recortado

            face_saved = cv2.imwrite(
                face_image_path,
                face_roi_bw
            )

            # Salvar imagem completa

            full_saved = cv2.imwrite(
                full_image_path,
                frame_bw
            )

            # Confirmar gravação

            if face_saved and full_saved:

                sample += 1

                print(
                    "=> Photo " +
                    str(sample) +
                    " saved successfully!"
                )

                print("Face:", face_image_path)
                print("Full image:", full_image_path)

            else:

                print("Error saving photo.")
                print("Face saved:", face_saved)
                print("Full image saved:", full_saved)

            # Mostrar rosto capturado em preto e branco

            cv2.imshow(
                "Captured face",
                face_roi_bw
            )

        else:

            print("No face detected. Try again.")

    # ======================================
    # FECHAR COM ESC
    # ======================================

    if key == 27:

        print("Capture interrupted.")
        break

    # Fechar se a janela for fechada pelo X

    if cv2.getWindowProperty(
        "Capturing face",
        cv2.WND_PROP_VISIBLE
    ) < 1:

        print("Window closed.")
        break

    # Finalizar após 10 fotografias

    if sample >= max_samples:

        print("Maximum number of photos reached.")
        break


# ==========================================
# FINALIZAÇÃO
# ==========================================

print("Completed!")
print("Total photos saved:", sample)

cam.release()

cv2.destroyAllWindows()
