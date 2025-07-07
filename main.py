import os
from datetime import datetime
from src.preparacao_dados import preparar_dados_completo
from src.treinamento_modelo import executar_pipeline_completo
from src.visualizacao import salvar_relatorio_completo, salvar_dados_processados
from src.utils.arquivos import criar_diretorio


# Configurações
ARQUIVO_DADOS = 'data/dataset-scout-frc-2023.csv'
PASTA_RESULTADOS = 'results'
PASTA_FIGURAS = 'figuras'


def executar_analise():
    """Executa análise completa dos dados FRC 2023."""
    print("=" * 60)
    print("  ANÁLISE DE MINERAÇÃO DE DADOS - FRC 2023")
    print("=" * 60)

    # Criar diretórios necessários
    criar_diretorio(PASTA_RESULTADOS)
    criar_diretorio(PASTA_FIGURAS)

    try:
        # Etapa 1: Preparação dos dados
        print("\n[1/4] Carregando e preparando dados...")
        dados, metricas_preparacao = preparar_dados_completo(ARQUIVO_DADOS)
        print(f"  ✓ {len(dados)} registros carregados")
        print(f"  ✓ {len(metricas_preparacao)} métricas calculadas")

        # Etapa 2: Treinamento dos modelos
        print("\n[2/4] Treinando modelos de mineração...")
        resultados_modelo = executar_pipeline_completo(dados)

        n_clusters = len(resultados_modelo['analises']['clusters'])
        acuracia = resultados_modelo['insights']['AcuraciaPrevisaoVitoria']
        print(f"  ✓ {n_clusters} clusters identificados")
        print(f"  ✓ Modelo de classificação treinado (acurácia: {acuracia})")

        # Etapa 3: Salvando resultados
        print("\n[3/4] Salvando resultados...")


        # Arquivo principal de resultados
        arquivo_relatorio = os.path.join(PASTA_RESULTADOS, 'relatorio_mineracao_frc2023.txt')
        salvar_relatorio_completo(arquivo_relatorio, metricas_preparacao, resultados_modelo)
        print(f"  ✓ Relatório salvo em: {arquivo_relatorio}")



        # Dados processados
        salvar_dados_processados(PASTA_RESULTADOS, dados, resultados_modelo)
        print(f"  ✓ Dados processados salvos em: {PASTA_RESULTADOS}/")

        # Etapa 4: Resumo final
        print("\n[4/4] Análise concluída!")
        print("\n" + "-" * 60)
        print("  RESUMO DOS RESULTADOS:")
        print("-" * 60)

        # Exibir principais métricas
        print(f"\n  Métricas do Evento:")
        for metrica, valor in list(metricas_preparacao.items())[:5]:
            print(f"  • {metrica}: {valor}")

        print(f"\n  Insights dos Modelos:")
        for insight, valor in list(resultados_modelo['insights'].items())[:5]:
            print(f"  • {insight}: {valor}")

        print("\n" + "=" * 60)
        print("  Análise finalizada com sucesso!")
        print(f"  Verifique os resultados em: {PASTA_RESULTADOS}/")
        print("=" * 60)

        return True

    except FileNotFoundError:
        print(f"\n[ERRO] Arquivo não encontrado: {ARQUIVO_DADOS}")
        print("  Verifique se o arquivo está na pasta 'data/'")
        return False

    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro durante a análise:")
        print(f"  {type(e).__name__}: {str(e)}")
        return False


def main():
    """Função principal."""
    inicio = datetime.now()

    sucesso = executar_analise()

    fim = datetime.now()
    tempo_total = (fim - inicio).total_seconds()

    if sucesso:
        print(f"\nTempo total de execução: {tempo_total:.1f} segundos")

    return 0 if sucesso else 1


if __name__ == '__main__':
    exit(main())
