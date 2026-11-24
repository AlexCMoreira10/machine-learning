import cv2

print("Testando conexão com DroidCam...\n")

for backend in [
    cv2.CAP_ANY,
    cv2.CAP_DSHOW,
    cv2.CAP_MSMF
]:

    print("Testando backend:", backend)

    cam = cv2.VideoCapture(0, backend)

    if cam.isOpened():

        print("Câmera aberta!")

        ret, frame = cam.read()

        if ret:
            print("Imagem recebida:", frame.shape)
        else:
            print("Câmera abriu, mas não recebeu imagem.")

    else:

        print("Não foi possível abrir.")

    cam.release()

    print("-------------------------")