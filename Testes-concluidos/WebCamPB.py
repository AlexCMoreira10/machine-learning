import cv2;
camera = cv2.VideoCapture(0);

while (True):
    conectado, imagem = camera.read()
    imagem = cv2 .cvtColor
    cv2.imshow("Face", imagem)

    # Aguarda 1ms para capturar a tecla pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    #Permite Fechar a janela com o botão de fechar
    if cv2.getWindowProperty("Face", cv2.WND_PROP_VISIBLE) < 1:
        break
    cv2.waitKey(1)
camera.release()
cv2.destroyAllWindow()
