import cv2;

detector_facial = cv2.CascadeClassifier(
    cv2.data.haarcascades + "../Treinamento/haarcascade_frontalface_default.xml"
)
camera = cv2.VideoCapture(0)
while (True):
    conectado, imagem = camera.read()
    #imagem = cv2 .cvtColor(imagem, cv2.COLOR_BGR2GRAY)  # Converte a imagem para escala de cinza
    cv2.imshow("Face", imagem)

    # Aguarda 1ms p ara capturar a tecla pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    #Permite Fechar a janela com o botão de fechar
    if cv2.getWindowProperty("Face", cv2.WND_PROP_VISIBLE) < 1:
        break
    cv2.waitKey(1)
camera.release()
cv2.destroyAllWindow()
