import pandas as pd
import numpy as np


def carregar_dados(caminho_arquivo):
    """Carrega dados do CSV do FRC 2023."""
    dados = pd.read_csv(caminho_arquivo, encoding='utf-8')
    return dados


def limpar_penalidades(dados):
    """Corrige a coluna de penalidades, convertendo 'o' para '0' e vazios para 0."""
    coluna_penalidade = 'Pontuação de penalidade da aliança oposta:'

    # Converter para string primeiro para manipulação
    dados[coluna_penalidade] = dados[coluna_penalidade].astype(str)

    # Substituir 'o' por '0'
    dados[coluna_penalidade] = dados[coluna_penalidade].str.replace('o', '0', case=False)

    # Substituir vazios, 'nan' ou espaços por '0'
    dados[coluna_penalidade] = dados[coluna_penalidade].replace(['nan', '', ' ', 'NaN'], '0')

    # Converter para inteiro
    dados[coluna_penalidade] = pd.to_numeric(dados[coluna_penalidade], errors='coerce').fillna(0).astype(int)

    return dados


def traduzir_colunas(dados):
    """Traduz nomes das colunas para facilitar análise."""
    traducoes = {
        'Carimbo de data/hora': 'data_hora',
        'Avaliador': 'avaliador',
        'Equipe avaliada': 'equipe',
        'Aliança': 'alianca',
        'Partida:': 'partida',
        'Robô operacional': 'robo_operacional',
        'Mobilidade (autônomo)': 'auto_mobilidade',
        'Peças de jogo (autônomo): \nPontuou na ROW inferior': 'auto_row_inferior',
        'Peças de jogo (autônomo): \nPontuou na ROW do meio': 'auto_row_meio',
        'Peças de jogo (autônomo): \nPontuou na ROW do topo': 'auto_row_topo',
        'Robô contato com a charge station (autonômo):': 'auto_charge_station',
        'Peças de jogo (teleoperado): \nPontuou na ROW inferior': 'tele_row_inferior',
        'Peças de jogo (teleoperado): \nPontuou na ROW do meio': 'tele_row_meio',
        'Peças de jogo (teleoperado): \nPontuou na ROW do topo': 'tele_row_topo',
        'Robô contato com a charge station (teleoperado):': 'tele_charge_station',
        'Link (teleoperado):\n3 NODES adjacentes com peças de jogo pontuando': 'links',
        'Park (teleoperado):\nTodos os bumpers do robô dentro da sua comunidade sem estar DOCKED': 'estacionado',
        'Coopertion bonus (qualificatória):\nAo menos 3 PEÇAS DE JOGO foram pontuadas em cada CO-OP GRID da aliança': 'bonus_cooperacao',
        'Activation bonus (qualificatória):\nAo menos 26 pontos foram ganhos com a CHARGE STATION durante o período autonômo e/ou endgame': 'bonus_ativacao',
        'Resultado final (qualificatória):': 'resultado',
        'Pontuação de penalidade da aliança oposta:': 'penalidades_oponente'
    }

    dados.rename(columns=traducoes, inplace=True)
    return dados


def criar_features_derivadas(dados):
    """Cria features adicionais para análise."""
    # Total de peças no autônomo
    dados['total_pecas_auto'] = (
        dados['auto_row_inferior'] +
        dados['auto_row_meio'] +
        dados['auto_row_topo']
    )

    # Total de peças no teleoperado
    dados['total_pecas_tele'] = (
        dados['tele_row_inferior'] +
        dados['tele_row_meio'] +
        dados['tele_row_topo']
    )

    # Total geral de peças
    dados['total_pecas'] = dados['total_pecas_auto'] + dados['total_pecas_tele']

    # Pontuação aproximada no autônomo (valores do jogo 2023)
    dados['pontos_auto'] = (
        dados['auto_row_inferior'] * 3 +
        dados['auto_row_meio'] * 4 +
        dados['auto_row_topo'] * 6
    )

    # Pontuação aproximada no teleoperado
    dados['pontos_tele'] = (
        dados['tele_row_inferior'] * 2 +
        dados['tele_row_meio'] * 3 +
        dados['tele_row_topo'] * 5
    )

    # Indicador de vitória (1 para vitória, 0 para derrota)
    dados['vitoria'] = (dados['resultado'] == 'Vitória').astype(int)

    return dados


def calcular_metricas_analise(dados):
    """Calcula as métricas solicitadas para o relatório."""
    metricas = {}

    # EquipeComMaiorTaxaDeVitoria
    taxa_vitoria_equipe = dados.groupby('equipe').agg({
        'vitoria': ['sum', 'count']
    })
    taxa_vitoria_equipe.columns = ['vitorias', 'partidas']
    taxa_vitoria_equipe['taxa_vitoria'] = taxa_vitoria_equipe['vitorias'] / taxa_vitoria_equipe['partidas']
    taxa_vitoria_equipe = taxa_vitoria_equipe[taxa_vitoria_equipe['partidas'] >= 3]  # Mínimo 3 partidas

    if not taxa_vitoria_equipe.empty:
        equipe_top = taxa_vitoria_equipe['taxa_vitoria'].idxmax()
        taxa_top = taxa_vitoria_equipe.loc[equipe_top, 'taxa_vitoria']
        metricas['EquipeComMaiorTaxaDeVitoria'] = f"{equipe_top} ({taxa_top:.1%})"

    # AliancaComMaiorTaxaDeVitoria
    taxa_vitoria_alianca = dados.groupby('alianca')['vitoria'].mean()
    alianca_top = taxa_vitoria_alianca.idxmax()
    metricas['AliancaComMaiorTaxaDeVitoria'] = f"{alianca_top} ({taxa_vitoria_alianca[alianca_top]:.1%})"

    # TotalDePecasPontuadasNasROWS
    total_pecas = (
        dados['auto_row_inferior'].sum() + dados['auto_row_meio'].sum() +
        dados['auto_row_topo'].sum() + dados['tele_row_inferior'].sum() +
        dados['tele_row_meio'].sum() + dados['tele_row_topo'].sum()
    )
    metricas['TotalDePecasPontuadasNasROWS'] = int(total_pecas)

    # ROWmaisComumenteUtilizada e ROWmenosComumenteUtilizada
    rows_totais = {
        'Inferior': dados['auto_row_inferior'].sum() + dados['tele_row_inferior'].sum(),
        'Meio': dados['auto_row_meio'].sum() + dados['tele_row_meio'].sum(),
        'Topo': dados['auto_row_topo'].sum() + dados['tele_row_topo'].sum()
    }

    row_mais_usada = max(rows_totais, key=rows_totais.get)
    row_menos_usada = min(rows_totais, key=rows_totais.get)

    metricas['ROWmaisComumenteUtilizada'] = f"{row_mais_usada} ({rows_totais[row_mais_usada]} peças)"
    metricas['ROWmenosComumenteUtilizada'] = f"{row_menos_usada} ({rows_totais[row_menos_usada]} peças)"

    # ROWmaisUtilizadaEmRelacaoAsVitorias
    vitorias_df = dados[dados['vitoria'] == 1]
    rows_vitorias = {
        'Inferior': vitorias_df['auto_row_inferior'].sum() + vitorias_df['tele_row_inferior'].sum(),
        'Meio': vitorias_df['auto_row_meio'].sum() + vitorias_df['tele_row_meio'].sum(),
        'Topo': vitorias_df['auto_row_topo'].sum() + vitorias_df['tele_row_topo'].sum()
    }

    row_mais_vitoriosa = max(rows_vitorias, key=rows_vitorias.get)
    metricas['ROWmaisUtilizadaEmRelacaoAsVitorias'] = f"{row_mais_vitoriosa} ({rows_vitorias[row_mais_vitoriosa]} peças em vitórias)"

    # PontuacaoAutonomoMaisAlta
    pontos_auto_equipe = dados.groupby('equipe')['pontos_auto'].max()
    equipe_auto_max = pontos_auto_equipe.idxmax()
    metricas['PontuacaoAutonomoMaisAlta'] = f"{equipe_auto_max} ({int(pontos_auto_equipe[equipe_auto_max])} pontos)"

    # PontuacaoTeleoperadoMaisAlta
    pontos_tele_equipe = dados.groupby('equipe')['pontos_tele'].max()
    equipe_tele_max = pontos_tele_equipe.idxmax()
    metricas['PontuacaoTeleoperadoMaisAlta'] = f"{equipe_tele_max} ({int(pontos_tele_equipe[equipe_tele_max])} pontos)"

    # RelacaoChargeStationVitoria
    charge_auto_vitoria = dados[dados['auto_charge_station'].isin(['Engajado', 'Docked'])]['vitoria'].mean()
    charge_tele_vitoria = dados[dados['tele_charge_station'].isin(['Engajado', 'Docked'])]['vitoria'].mean()
    sem_charge_vitoria = dados[
        (~dados['auto_charge_station'].isin(['Engajado', 'Docked'])) &
        (~dados['tele_charge_station'].isin(['Engajado', 'Docked']))
    ]['vitoria'].mean()

    metricas['RelacaoChargeStationVitoria'] = (
        f"Com charge station: {charge_auto_vitoria:.1%} (auto) / "
        f"{charge_tele_vitoria:.1%} (tele) | Sem: {sem_charge_vitoria:.1%}"
    )

    return metricas


def preparar_dados_completo(caminho_arquivo):
    """Executa todo o pipeline de preparação de dados."""
    dados = carregar_dados(caminho_arquivo)
    dados = limpar_penalidades(dados)
    dados = traduzir_colunas(dados)
    dados = criar_features_derivadas(dados)

    return dados, calcular_metricas_analise(dados)
