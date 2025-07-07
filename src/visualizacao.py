import os
from datetime import datetime


def criar_separador(tamanho=60, caractere='-'):
    """Cria linha separadora para formatação."""
    return caractere * tamanho


def formatar_tabela_texto(dados, titulo, colunas_exibir=None):
    """Formata dataframe como tabela de texto."""
    texto = []
    texto.append(criar_separador())
    texto.append(f"  {titulo}")
    texto.append(criar_separador())

    if colunas_exibir:
        dados_exibir = dados[colunas_exibir]
    else:
        dados_exibir = dados

    # Cabeçalho
    colunas = list(dados_exibir.columns)
    larguras = {}
    for col in colunas:
        largura_col = max(len(str(col)), dados_exibir[col].astype(str).str.len().max())
        larguras[col] = min(largura_col, 20)  # Limite máximo

    # Linha de cabeçalho
    linha_header = "  "
    for col in colunas:
        linha_header += str(col).ljust(larguras[col] + 2)
    texto.append(linha_header)
    texto.append("  " + "-" * (sum(larguras.values()) + len(colunas) * 2))

    # Dados
    for _, row in dados_exibir.iterrows():
        linha = "  "
        for col in colunas:
            valor = str(row[col])
            if len(valor) > larguras[col]:
                valor = valor[:larguras[col]-3] + "..."
            linha += valor.ljust(larguras[col] + 2)
        texto.append(linha)

    texto.append(criar_separador())
    return "\n".join(texto)


def criar_resumo_clusters(analise_clusters):
    """Cria resumo visual dos clusters em texto."""
    texto = []
    texto.append("\n" + criar_separador(60, '='))
    texto.append("  ANÁLISE DE CLUSTERS - PERFIS DE EQUIPES")
    texto.append(criar_separador(60, '='))

    for idx, row in analise_clusters.iterrows():
        texto.append(f"\n  Cluster {idx}: {row['tipo_equipe']}")
        texto.append("  " + "-" * 40)
        texto.append(f"  • Número de equipes: {int(row['num_equipes'])}")
        texto.append(f"  • Taxa de vitória: {row['vitoria']:.1%}")
        texto.append(f"  • Pontos autônomo (média): {row['pontos_auto']:.1f}")
        texto.append(f"  • Pontos teleoperado (média): {row['pontos_tele']:.1f}")
        texto.append(f"  • Total de peças (média): {row['total_pecas']:.1f}")
        texto.append(f"  • Links pontuados (média): {row['links']:.2f}")

        # Característica especial do cluster
        if row['tipo_equipe'] == 'Elite':
            texto.append("  → Desempenho excepcional em todas as áreas")
        elif row['tipo_equipe'] == 'Especialista Autônomo':
            texto.append("  → Forte início de partida com pontuação autônoma")
        elif row['tipo_equipe'] == 'Especialista Teleoperado':
            texto.append("  → Excelente controle manual e pontuação")
        elif row['tipo_equipe'] == 'Estrategista de Links':
            texto.append("  → Foco em completar links para pontos bônus")

    return "\n".join(texto)


def criar_ranking_importancia_features(importancias, top_n=10):
    """Cria ranking visual de importância das features."""
    texto = []
    texto.append("\n" + criar_separador(60, '='))
    texto.append("  FATORES MAIS IMPORTANTES PARA VITÓRIA")
    texto.append(criar_separador(60, '='))

    for idx, (_, row) in enumerate(importancias.head(top_n).iterrows(), 1):
        feature_nome = traduzir_nome_feature(row['feature'])
        importancia = row['importancia'] * 100

        # Barra visual
        barra_tamanho = int(importancia / 2)
        barra = "█" * barra_tamanho

        texto.append(f"\n  {idx}. {feature_nome}")
        texto.append(f"     {barra} {importancia:.1f}%")

    return "\n".join(texto)


def traduzir_nome_feature(nome):
    """Traduz nomes técnicos das features para português claro."""
    traducoes = {
        'pontos_tele': 'Pontuação no Teleoperado',
        'pontos_auto': 'Pontuação no Autônomo',
        'total_pecas': 'Total de Peças Pontuadas',
        'total_pecas_tele': 'Peças no Teleoperado',
        'total_pecas_auto': 'Peças no Autônomo',
        'links': 'Links Completados',
        'penalidades_oponente': 'Penalidades do Oponente',
        'teve_auto_charge': 'Charge Station no Autônomo',
        'teve_tele_charge': 'Charge Station no Teleoperado',
        'prop_row_alta': 'Proporção de Peças no Topo'
    }
    return traducoes.get(nome, nome.replace('_', ' ').title())


def criar_resumo_modelo_classificacao(relatorio):
    """Cria resumo do desempenho do modelo de classificação."""
    texto = []
    texto.append("\n" + criar_separador(60, '='))
    texto.append("  DESEMPENHO DO MODELO DE PREVISÃO")
    texto.append(criar_separador(60, '='))

    texto.append(f"\n  Acurácia Geral: {relatorio['accuracy']:.1%}")
    texto.append("\n  Detalhamento por Classe:")

    # Verificar se as métricas existem antes de acessar
    if '0' in relatorio:
        texto.append("\n  → Previsão de DERROTA:")
        texto.append(f"    • Precisão: {relatorio['0']['precision']:.1%}")
        texto.append(f"    • Recall: {relatorio['0']['recall']:.1%}")
        texto.append(f"    • F1-Score: {relatorio['0']['f1-score']:.1%}")

    if '1' in relatorio:
        texto.append("\n  → Previsão de VITÓRIA:")
        texto.append(f"    • Precisão: {relatorio['1']['precision']:.1%}")
        texto.append(f"    • Recall: {relatorio['1']['recall']:.1%}")
        texto.append(f"    • F1-Score: {relatorio['1']['f1-score']:.1%}")

    return "\n".join(texto)


def criar_estatisticas_equipes(equipes_cluster, top_n=10):
    """Cria estatísticas das top equipes."""
    texto = []
    texto.append("\n" + criar_separador(60, '='))
    texto.append("  TOP EQUIPES POR DESEMPENHO GERAL")
    texto.append(criar_separador(60, '='))

    # Criar score composto
    equipes_cluster['score_geral'] = (
        equipes_cluster['vitoria'] * 100 +
        equipes_cluster['pontos_auto'] / 10 +
        equipes_cluster['pontos_tele'] / 10 +
        equipes_cluster['links'] * 5
    )

    top_equipes = equipes_cluster.nlargest(top_n, 'score_geral')

    for idx, (_, row) in enumerate(top_equipes.iterrows(), 1):
        tipo_cluster = row.get('tipo_equipe', 'N/A')
        texto.append(f"\n  {idx}. Equipe {row['equipe']}")
        texto.append(f"     • Perfil: {tipo_cluster}")
        texto.append(f"     • Taxa de vitória: {row['vitoria']:.1%}")
        texto.append(f"     • Média pontos/partida: {(row['pontos_auto'] + row['pontos_tele']):.1f}")

    return "\n".join(texto)


def salvar_relatorio_completo(caminho_saida, metricas_preparacao, resultados_modelo):
    """Salva relatório completo em arquivo de texto."""
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        # Cabeçalho
        f.write(criar_separador(60, '=') + "\n")
        f.write("  RELATÓRIO DE MINERAÇÃO DE DADOS - FRC 2023\n")
        f.write(f"  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(criar_separador(60, '=') + "\n")

        # Métricas da preparação de dados
        f.write("\n" + criar_separador(60, '-') + "\n")
        f.write("  MÉTRICAS GERAIS DO EVENTO\n")
        f.write(criar_separador(60, '-') + "\n")

        for metrica, valor in metricas_preparacao.items():
            f.write(f"  [{metrica}]: {valor}\n")

        # Insights do modelo
        if 'insights' in resultados_modelo:
            f.write("\n" + criar_separador(60, '-') + "\n")
            f.write("  INSIGHTS DOS MODELOS DE MINERAÇÃO\n")
            f.write(criar_separador(60, '-') + "\n")

            for insight, valor in resultados_modelo['insights'].items():
                f.write(f"  [{insight}]: {valor}\n")

        # Análise de clusters
        if 'analises' in resultados_modelo:
            f.write(criar_resumo_clusters(resultados_modelo['analises']['clusters']))

            # Ranking de importância
            f.write(criar_ranking_importancia_features(
                resultados_modelo['analises']['importancia_features']
            ))

            # Desempenho do modelo
            f.write(criar_resumo_modelo_classificacao(
                resultados_modelo['analises']['relatorio_classificacao']
            ))

            # Top equipes
            f.write(criar_estatisticas_equipes(
                resultados_modelo['analises']['equipes_cluster']
            ))

        # Rodapé
        f.write("\n" + criar_separador(60, '=') + "\n")
        f.write("  FIM DO RELATÓRIO\n")
        f.write(criar_separador(60, '=') + "\n")


def salvar_dados_processados(caminho_pasta, dados, resultados_modelo):
    """Salva dados processados em formato CSV."""
    os.makedirs(caminho_pasta, exist_ok=True)

    # Salvar dados com clusters
    if 'analises' in resultados_modelo and 'equipes_cluster' in resultados_modelo['analises']:
        equipes_cluster = resultados_modelo['analises']['equipes_cluster']
        equipes_cluster.to_csv(
            os.path.join(caminho_pasta, 'equipes_com_clusters.csv'),
            index=False,
            encoding='utf-8'
        )

    # Salvar resumo de clusters
    if 'analises' in resultados_modelo and 'clusters' in resultados_modelo['analises']:
        resultados_modelo['analises']['clusters'].to_csv(
            os.path.join(caminho_pasta, 'resumo_clusters.csv'),
            index=True,
            encoding='utf-8'
        )

    # Salvar importância de features
    if 'analises' in resultados_modelo and 'importancia_features' in resultados_modelo['analises']:
        resultados_modelo['analises']['importancia_features'].to_csv(
            os.path.join(caminho_pasta, 'importancia_features.csv'),
            index=False,
            encoding='utf-8'
        )
