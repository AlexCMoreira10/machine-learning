
import cv2
import time
from pathlib import Path


class CapturaFacial:
    def __init__(self):
        self.total_fotos = 11
        self.intervalo = 1.0
        self.ultima_captura = 0

        self.fotos = []

        pasta_modelos = (
            Path(__file__).resolve().parents[1] / "Modelos"
        )

        self.detector = cv2.dnn.readNetFromCaffe(
            str(pasta_modelos / "deploy.prototxt.txt"),
            str(
                pasta_modelos /
                "res10_300x300_ssd_iter_140000.caffemodel"
            )
        )

    def processar(self, imagem):
        altura, largura = imagem.shape[:2]

        blob = cv2.dnn.blobFromImage(
            imagem,
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )

        self.detector.setInput(blob)
        deteccoes = self.detector.forward()

        rostos = []

        for i in range(deteccoes.shape[2]):
            confianca = float(deteccoes[0, 0, i, 2])

            if confianca < 0.85:
                continue

            caixa = deteccoes[0, 0, i, 3:7] * [
                largura, altura, largura, altura
            ]

            x1, y1, x2, y2 = caixa.astype(int)

            x1 = max(0, min(x1, largura))
            x2 = max(0, min(x2, largura))
            y1 = max(0, min(y1, altura))
            y2 = max(0, min(y2, altura))

            if x2 - x1 < 105 or y2 - y1 < 105:
                continue

            rostos.append((x1, y1, x2, y2))

        # Exige exatamente um rosto
        if len(rostos) != 1:
            return imagem, len(self.fotos)

        x1, y1, x2, y2 = rostos[0]

        cv2.rectangle(
            imagem,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        agora = time.monotonic()

        if (
            len(self.fotos) < self.total_fotos
            and agora - self.ultima_captura >= self.intervalo
        ):
            rosto = imagem[y1:y2, x1:x2]

            rosto_cinza = cv2.cvtColor(
                rosto, cv2.COLOR_BGR2GRAY
            )

            rosto_cinza = cv2.resize(
                rosto_cinza,
                (90, 120)
            )

            self.fotos.append(rosto_cinza.copy())
            self.ultima_captura = agora

        return imagem, len(self.fotos)

    def concluido(self):
        return len(self.fotos) >= self.total_fotos


def processar_foto_importada(caminho_imagem, detector_facial):
    import numpy as np

    # 1. Carregar imagem
    dados = np.fromfile(str(caminho_imagem), dtype=np.uint8)
    imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR)

    if imagem is None:
        raise ValueError("Não foi possível abrir a imagem.")

    altura, largura = imagem.shape[:2]

    # 2. Preparar imagem para o SSD
    blob = cv2.dnn.blobFromImage(
        imagem,
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 177.0, 123.0)
    )

    detector_facial.setInput(blob)
    deteccoes = detector_facial.forward()

    # 3. Coletar detecções e suas confianças
    rostos = []

    for i in range(deteccoes.shape[2]):
        confianca = float(deteccoes[0, 0, i, 2])

        if confianca < 0.85:
            continue

        caixa = deteccoes[0, 0, i, 3:7] * np.array(
            [largura, altura, largura, altura]
        )

        x1, y1, x2, y2 = caixa.astype(int)

        x1 = max(0, min(x1, largura))
        x2 = max(0, min(x2, largura))
        y1 = max(0, min(y1, altura))
        y2 = max(0, min(y2, altura))

        if x2 <= x1 or y2 <= y1:
            continue

        rostos.append({
            "caixa": (x1, y1, x2, y2),
            "confianca": confianca
        })

    if not rostos:
        raise ValueError("Nenhum rosto encontrado na fotografia.")

    # 4. Ordenar por confiança (maior primeiro)
    rostos.sort(
        key=lambda rosto: rosto["confianca"],
        reverse=True
    )

    # 5. Calcular sobreposição entre caixas
    def calcular_iou(caixa_a, caixa_b):
        ax1, ay1, ax2, ay2 = caixa_a
        bx1, by1, bx2, by2 = caixa_b

        x1 = max(ax1, bx1)
        y1 = max(ay1, by1)
        x2 = min(ax2, bx2)
        y2 = min(ay2, by2)

        intersecao = (
            max(0, x2 - x1) *
            max(0, y2 - y1)
        )

        area_a = (ax2 - ax1) * (ay2 - ay1)
        area_b = (bx2 - bx1) * (by2 - by1)

        uniao = area_a + area_b - intersecao

        return intersecao / uniao if uniao > 0 else 0

    # 6. Agrupar detecções do mesmo rosto
    rostos_filtrados = []

    for rosto in rostos:
        x1, y1, x2, y2 = rosto["caixa"]

        centro_x = (x1 + x2) / 2
        centro_y = (y1 + y2) / 2

        duplicado = False

        for existente in rostos_filtrados:
            ex1, ey1, ex2, ey2 = existente["caixa"]

            centro_ex = (ex1 + ex2) / 2
            centro_ey = (ey1 + ey2) / 2

            largura_media = (
                (x2 - x1) + (ex2 - ex1)
            ) / 2

            altura_media = (
                (y2 - y1) + (ey2 - ey1)
            ) / 2

            centros_proximos = (
                abs(centro_x - centro_ex) < largura_media * 0.6
                and
                abs(centro_y - centro_ey) < altura_media * 0.6
            )

            sobreposicao = calcular_iou(
                rosto["caixa"],
                existente["caixa"]
            )

            if centros_proximos or sobreposicao > 0.5:
                duplicado = True
                break

        if not duplicado:
            rostos_filtrados.append(rosto)

    # 7. Verificar quantos rostos distintos restaram
    print(f"\nImagem: {caminho_imagem}")
    print(f"Detecções SSD: {len(rostos)}")
    print(f"Rostos após filtragem: {len(rostos_filtrados)}")

    for rosto in rostos_filtrados:
        print(
            f"Confiança: {rosto['confianca']:.3f} | "
            f"Caixa: {rosto['caixa']}"
        )

    if len(rostos_filtrados) != 1:
        raise ValueError(
            "Não foi possível identificar um único rosto "
            f"com segurança. Detecções restantes: "
            f"{len(rostos_filtrados)}."
        )

    # 8. Selecionar o rosto de maior confiança
    x1, y1, x2, y2 = rostos_filtrados[0]["caixa"]

    rosto = imagem[y1:y2, x1:x2]

    if rosto.size == 0:
        raise ValueError("O recorte facial ficou vazio.")

    # 9. Converter para preto e branco
    rosto_cinza = cv2.cvtColor(
        rosto,
        cv2.COLOR_BGR2GRAY
    )

    # 10. Padronizar para o Eigenfaces
    rosto_cinza = cv2.resize(
        rosto_cinza,
        (90, 120),
        interpolation=cv2.INTER_AREA
    )

    return rosto_cinza
