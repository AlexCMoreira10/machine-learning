
import customtkinter as ctk
import cv2
from PIL import Image

from interface.captura_facial import CapturaFacial


class JanelaCapturaFacial(ctk.CTkToplevel):

    def __init__(self, master, ao_concluir):
        super().__init__(master)

        self.title("FaceGate - Captura facial")
        self.geometry("720x600")

        self.ao_concluir = ao_concluir
        self.camera = None
        self.atualizacao_id = None
        self.finalizado = False

        self.captura = CapturaFacial()

        self.label_camera = ctk.CTkLabel(
            self,
            text="Iniciando câmera...",
            width=640,
            height=400
        )
        self.label_camera.pack(pady=20)

        self.label_contador = ctk.CTkLabel(
            self,
            text="Fotos capturadas: 0/11",
            font=("Arial", 18, "bold")
        )
        self.label_contador.pack(pady=10)

        self.label_orientacao = ctk.CTkLabel(
            self,
            text="Olhe para a câmera e mova levemente o rosto."
        )
        self.label_orientacao.pack(pady=10)

        ctk.CTkButton(
            self,
            text="Cancelar",
            command=self.fechar
        ).pack(pady=15)

        self.protocol("WM_DELETE_WINDOW", self.fechar)

        self.after(100, self.iniciar_camera)

    def iniciar_camera(self):
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            self.label_orientacao.configure(
                text="Não foi possível abrir a webcam."
            )
            self.camera.release()
            self.camera = None
            return

        self.atualizar_camera()

    def atualizar_camera(self):
        self.atualizacao_id = None

        if self.finalizado or self.camera is None:
            return

        conectado, imagem = self.camera.read()

        if conectado:
            imagem, quantidade = self.captura.processar(imagem)

            self.label_contador.configure(
                text=f"Fotos capturadas: {quantidade}/11"
            )

            imagem_rgb = cv2.cvtColor(
                imagem, cv2.COLOR_BGR2RGB
            )

            imagem_pil = Image.fromarray(imagem_rgb)

            imagem_ctk = ctk.CTkImage(
                light_image=imagem_pil,
                dark_image=imagem_pil,
                size=(640, 400)
            )

            self.label_camera.configure(
                image=imagem_ctk,
                text=""
            )

            if self.captura.concluido():
                self.concluir()
                return

        self.atualizacao_id = self.after(
            30, self.atualizar_camera
        )

    def concluir(self):
        self.finalizado = True

        # Guarda as imagens antes de fechar a janela
        fotos = list(self.captura.fotos)

        self.liberar_camera()
        self.destroy()

        self.ao_concluir(fotos)

    def liberar_camera(self):
        if self.atualizacao_id is not None:
            self.after_cancel(self.atualizacao_id)
            self.atualizacao_id = None

        if self.camera is not None:
            self.camera.release()
            self.camera = None

    def fechar(self):
        self.finalizado = True
        self.liberar_camera()
        self.destroy()
