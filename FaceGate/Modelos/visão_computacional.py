import cv2

imagem = cv2.imread('/home/alex/Documentos/Machine Learning/Visao Computacional/Imagens/alex-allan.png') #caminho absoluto

if imagem is None:
    raise FileNotFoundError('Imagem não encontrada. verifique o caminho')
print("As dimensões da imagem altura, largura e canais:", imagem.shape)

# Convertendo a image de COLORIDA para tons de CINZA
# POR QUÊ é necasserio mudar o tom da imagem?
# - Uma imagem colorida geralmente possui três canais de cor. Ao converter-la para escalas de cinza passamos a trabalhar
# - com um único canal, que representa a intensidade luminosa dos pixels.
# - Isso é util porque o classificador Haar utilizado no codigo foi projetado para analisar caracteristicas de intesidade e contraste,
# - e não para precisa das informações de cor da imagem.
# - A conversão não significa simplesmente retirar um canal: o OpenCV calcula a intensidade de cinza a partir dos valores dos canais BGR.
imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

# Carregando o CLASSIFICADOR
# arquivo haarcascade?
# - Nele contém os dados de um classificador em cascata basedo em caracteristicas Haar, utilizados para detectar facer Frontais
# - Ele não é um modelo de rede neural profunda. É a uma abordagem clássica de visão computacional que pode ser utilizado antes de
# - estudar mais afundo detectores baseados em redes neurais.
# -
detector_facial = cv2.CascadeClassifier('/home/alex/Documentos/Machine Learning/Visao Computacional/haarcascade_frontalface_default.xml')

#Adicionando um verificador para saber se o arquivo foi carrecado
if detector_facial.empty():
    raise FileNotFoundError("Não foi possivel carregar o classificador XML.")

# Deteccões aplicnado na imagem
# - O que acontece nessa etapa?
# - O mét#odo detectMultiScale() analisa a imagem procurando regiões que correspondam ao classificador.
# - Ele pode procurar faces em diferentes escalas, o que permite detectar rostos de tamanhos variados.
# - O resultado é uma coleção de retângulos. Cada detecção contém quatro valores: (x, y, largura, altura)
deteccoes = detector_facial.detectMultiScale(imagem_cinza)

# Exibindo a quantidade de faces detecadas na imagem
# - lembrando que a quantidade de faces encontrada aqui
# - não necessariamente representa a quantidade de rostos de pessoas encontradas
# - já que pode detectar incorretamente outros valores.
print("Quantidade de faces encontrada: ",len(deteccoes))

# Desenhado os Retangulos na tela em cada face encontrada
for (x, y, largura, altura) in deteccoes:
    cv2.rectangle(
        imagem, #imagem_cinza, #aqui estou carregando a imagem
        (x, y), #canto superior esquerdo.
        (x + largura, y + altura),  # canto inferior direito.
        (0, 255, 0), # Cor dos retangulos
        4 #espessura da linha
    )

#Abrir imagemt
cv2.imshow("Minha Imagem", imagem)

# Aguarda uma tecla para fechar a janela
cv2.waitKey(0)
cv2.destroyAllWindows()