import cv2
import os
import pickle

# Diretório do arquivo atual
base_dir = os.path.dirname(os.path.abspath(__file__))

# Caminhos dos arquivos de treinamento
model_path = os.path.join(base_dir, "..", "Modelos", "eigen_classifier.yml")
names_path = os.path.join(base_dir, "..", "Modelos", "face_names.pickle")

# Carregando o modelo Eigenfaces
eigen_classifier = cv2.face.EigenFaceRecognizer_create()
eigen_classifier.read(model_path)

# Carregando a associação entre alunos e IDs
with open(names_path, "rb") as file:
    face_names = pickle.load(file)

print("Modelo Eigenfaces carregado!")
print("Alunos cadastrados:", face_names)

# Carregando o detector de rostos
#detector_path = os.path.join(
#    base_dir, "..", "Modelos", "haarcascade_frontalface_default.xml"
#)

# Caminhos dos arquivos do detector SSD
prototxt_path = os.path.join(
    base_dir, "..", "Modelos", "deploy.prototxt.txt"
)

ssd_model_path = os.path.join(
    base_dir, "..", "Modelos",
    "res10_300x300_ssd_iter_140000.caffemodel"
)

# Carregando o detector SSD
detector_facial = cv2.dnn.readNetFromCaffe(
    prototxt_path,
    ssd_model_path
)

print("Detector SSD carregado!")

#detector Haarcasde
#detector_facial = cv2.CascadeClassifier(detector_path)

# Inicializando a webcam
camera = cv2.VideoCapture(0, cv2.CAP_ANY)

if not camera.isOpened():
    print("Erro ao conectar à webcam.")
    exit()

print("Webcam conectada! Pressione Q para sair.")

while True:
    conectado, imagem = camera.read()

    if not conectado:
        print("Erro ao capturar imagem.")
        break

    # Convertendo a imagem para escala de cinza
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Detectando os rostos
    # Obtendo as dimensões da imagem da webcam
    altura, largura = imagem.shape[:2]

    # Preparando a imagem para o SSD
    blob = cv2.dnn.blobFromImage(
        imagem,
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 177.0, 123.0)
    )

    # Executando a detecção facial
    detector_facial.setInput(blob)
    deteccoes = detector_facial.forward()

    faces_detectadas = []

    for i in range(deteccoes.shape[2]):
        confianca_deteccao = float(deteccoes[0, 0, i, 2])

        if confianca_deteccao < 0.7:
            continue

        caixa = deteccoes[0, 0, i, 3:7] * [
            largura, altura, largura, altura
        ]

        x1, y1, x2, y2 = caixa.astype(int)

        # Mantendo as coordenadas dentro da imagem
        x1 = max(0, min(x1, largura))
        y1 = max(0, min(y1, altura))
        x2 = max(0, min(x2, largura))
        y2 = max(0, min(y2, altura))

        w = x2 - x1
        h = y2 - y1

        # Ignorando rostos pequenos ou caixas inválidas
        if w < 105 or h < 105:
            continue

        faces_detectadas.append((x1, y1, w, h))

    # Desenhando um retângulo em cada rosto detectado
    for (x, y, w, h) in faces_detectadas:

        # Recortando o rosto detectado
        rosto = imagem_cinza[y:y + h, x:x + w]

        # Ajustando ao tamanho utilizado no treinamento
        rosto = cv2.resize(rosto, (90, 120))

        # Realizando o reconhecimento
        id_reconhecido, confianca = eigen_classifier.predict(rosto)

        # Buscando o aluno correspondente ao ID
        nome_aluno = "Desconhecido"

        for nome, id_aluno in face_names.items():
            if id_aluno == id_reconhecido:
                nome_aluno = nome
                break

        # Exibindo o resultado na imagem
        cv2.rectangle(
            imagem,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            imagem,
            f"Aluno: {nome_aluno}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        print(f"ID: {id_reconhecido} | Aluno: {nome_aluno} | Distancia: {confianca:.2f}")
    cv2.imshow("FaceGate - Reconhecimento Facial", imagem)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()