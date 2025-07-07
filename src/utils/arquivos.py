import os


def criar_diretorio(caminho):
    """Cria diretório se não existir."""
    if not os.path.exists(caminho):
        os.makedirs(caminho)


def verificar_arquivo_existe(caminho):
    """Verifica se arquivo existe."""
    return os.path.isfile(caminho)


def listar_arquivos(pasta, extensao=None):
    """Lista arquivos em uma pasta."""
    if not os.path.exists(pasta):
        return []

    arquivos = []
    for arquivo in os.listdir(pasta):
        caminho_completo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_completo):
            if extensao is None or arquivo.endswith(extensao):
                arquivos.append(arquivo)

    return arquivos
