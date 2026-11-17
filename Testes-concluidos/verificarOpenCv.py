import cv2

camera_index = 0

print("Testando câmera...")

cam = cv2.VideoCapture(camera_index, cv2.CAP_ANY)

if cam.isOpened():
    print("Câmera conectada!")

    ret, frame = cam.read()

    if ret:
        print("Imagem capturada com sucesso!")
        cv2.imshow("Teste da camera", frame)
        cv2.waitKey(0)
    else:
        print("Câmera abriu, mas não capturou imagem.")

    cam.release()
    cv2.destroyAllWindows()

else:
    print("Não foi possível abrir a câmera.")