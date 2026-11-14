import cv2;

# Carregando o classificador facial
detector_facial = cv2.CascadeClassifier(
    cv2.data.haarcascades + "../Modelos/rehaarcascade_frontalface_default.xml"
)

while (True):
    conectado, imagem = camera.read()
    imagem = cv2 .cvtColor(imagem, cv2.COLOR_BGR2GRAY)  # Converte a imagem para escala de cinza
    cv2.imshow("Face", imagem)

    # Detectando rostos
    faces = detector_facial.detectMultiScale(
        imagem_cinza,
        scaleFactor=1.1,
        minNeighbors=5
    )

    # Desenhando um retângulo em cada rosto
    for (x, y, largura, altura) in faces:
        cv2.rectangle(
            imagem,
            (x, y),
            (x + largura, y + altura),
            (0, 255, 0),
            2
        )


    # Aguarda 1ms p ara capturar a tecla pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    #Permite Fechar a janela com o botão de fechar
    if cv2.getWindowProperty("Face", cv2.WND_PROP_VISIBLE) < 1:
        break
    cv2.waitKey(1)
camera.release()
cv2.destroyAllWindow()
