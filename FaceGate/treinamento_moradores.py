
import cv2
import json
import os
import tempfile

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

ARQUIVO_MORADORES = BASE_DIR / "dados" / "moradores.json"
PASTA_DATASET = BASE_DIR / "dataset_moradores"
PASTA_MODELOS = BASE_DIR / "modelos_moradores"

ARQUIVO_MODELO = PASTA_MODELOS / "eigen_classifier.yml"


def treinar_moradores():

    # 1. Carregar os moradores cadastrados
    with open(ARQUIVO_MORADORES, "r", encoding="utf-8") as arquivo:
        moradores = json.load(arquivo)

    imagens = []
    ids = []

    # 2. Percorrer apenas os moradores cadastrados
    for morador in moradores:

        id_facial = morador.get("id_facial")

        if id_facial is None:
            continue

        pasta_morador = PASTA_DATASET / str(id_facial)

        if not pasta_morador.is_dir():
            print(f"Imagens não encontradas para ID {id_facial}")
            continue

        fotos = sorted(pasta_morador.glob("foto_*.jpg"))

        if not 5 <= len(fotos) <= 11:
            print(
                f"ID {id_facial}: quantidade inválida "
                f"({len(fotos)} fotos). Esperado entre 5 e 11."
            )
            continue

        imagens_morador = []

        for caminho in fotos:
            imagem = cv2.imread(str(caminho), cv2.IMREAD_GRAYSCALE)

            if imagem is None:
                raise ValueError(f"Não foi possível ler {caminho}")

            imagem = cv2.resize(imagem, (90, 120))
            imagens_morador.append(imagem)

        imagens.extend(imagens_morador)
        ids.extend([int(id_facial)] * len(imagens_morador))

        print(f"Morador {morador['nome']}: {len(fotos)} fotos carregadas.")

    if not imagens:
        raise ValueError("Nenhuma imagem válida encontrada para treinamento.")

    # 3. Treinar o modelo Eigenfaces
    import numpy as np

    reconhecedor = cv2.face.EigenFaceRecognizer_create()

    reconhecedor.train(
        imagens,
        np.array(ids, dtype=np.int32)
    )

    # 4. Salvar o modelo em arquivo temporário
    PASTA_MODELOS.mkdir(parents=True, exist_ok=True)

    fd, caminho_temporario = tempfile.mkstemp(
        prefix="eigen_temp_",
        suffix=".yml",
        dir=PASTA_MODELOS
    )
    os.close(fd)

    try:
        reconhecedor.write(caminho_temporario)
        os.replace(caminho_temporario, ARQUIVO_MODELO)
    finally:
        if os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)

    print(f"Treinamento concluído: {len(imagens)} imagens.")
    print(f"Modelo salvo em: {ARQUIVO_MODELO}")

    return len(imagens)


if __name__ == "__main__":
    treinar_moradores()
