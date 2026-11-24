import cv2
import numpy as np
import os
from PIL import Image
import pickle

# Diretório onde está este arquivo Python
base_dir = os.path.dirname(os.path.abspath(__file__))

# Diretório das fotografias cadastradas
training_path = os.path.join(base_dir, "dataset")

print("Pasta de treinamento:", training_path)


def get_image_data(path_train):
    subdirs = [
        os.path.join(path_train, f)
        for f in os.listdir(path_train)
        if os.path.isdir(os.path.join(path_train, f))
    ]

    faces = []
    ids = []
    face_names = {}
    id = 1

    print("Pastas encontradas:")

    for subdir in sorted(subdirs):
        name = os.path.basename(subdir)

        face_names[name] = id

        print(f"Pasta: {name} | ID do treinamento: {id}")

        id += 1

def get_image_data(path_train):
    subdirs = [
        os.path.join(path_train, f)
        for f in os.listdir(path_train)
        if os.path.isdir(os.path.join(path_train, f))
    ]

    faces = []
    ids = []
    face_names = {}
    id = 1

    print("Carregando fotografias para treinamento...")

    for subdir in sorted(subdirs):
        name = os.path.basename(subdir)

        images_list = [
            os.path.join(subdir, f)
            for f in sorted(os.listdir(subdir))
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        if not images_list:
            continue

        face_names[name] = id

        for path in images_list:
            image = Image.open(path).convert("L")
            face = np.array(image, "uint8")
            face = cv2.resize(face, (90, 120))

            ids.append(id)
            faces.append(face)

            print(f"Aluno: {name} | ID: {id} | Foto: {os.path.basename(path)}")

        id += 1

    return np.array(ids), faces, face_names

ids, faces, face_names = get_image_data(training_path)

print("\nTotal de fotografias:", len(faces))
print("Identificações:", ids)
print("Alunos:", face_names)


# Treinamento do reconhecedor Eigenfaces
print("\nIniciando treinamento Eigenfaces...")

eigen_classifier = cv2.face.EigenFaceRecognizer_create()

eigen_classifier.train(faces, ids)

# Caminho para salvar o modelo treinado
model_path = os.path.join(base_dir, "..", "Modelos", "eigen_classifier.yml")

eigen_classifier.write(model_path)

print("Treinamento concluído!")
print("Modelo salvo em:", model_path)

# Salvando a associação entre alunos e IDs
names_path = os.path.join(base_dir, "..", "Modelos", "face_names.pickle")

with open(names_path, "wb") as file:
    pickle.dump(face_names, file)

print("Identificações dos alunos salvas!")
print("Arquivo salvo em:", names_path)