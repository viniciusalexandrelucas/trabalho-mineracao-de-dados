from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, silhouette_score
import numpy as np
import pandas as pd


def preparar_features_clustering(dados):
    """Prepara features para análise de clustering das equipes."""
    # Agregar dados por equipe
    features_equipe = dados.groupby('equipe').agg({
        'pontos_auto': 'mean',
        'pontos_tele': 'mean',
        'total_pecas': 'mean',
        'links': 'mean',
        'vitoria': 'mean',
        'auto_row_inferior': 'mean',
        'auto_row_meio': 'mean',
        'auto_row_topo': 'mean',
        'tele_row_inferior': 'mean',
        'tele_row_meio': 'mean',
        'tele_row_topo': 'mean'
    }).reset_index()

    # Features para clustering
    features_cols = [
        'pontos_auto', 'pontos_tele', 'total_pecas',
        'links', 'vitoria'
    ]

    X = features_equipe[features_cols]

    # Normalizar dados
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, features_equipe, scaler


def encontrar_numero_clusters_ideal(X_scaled, max_k=10):
    """Determina número ideal de clusters usando método do cotovelo e silhueta."""
    inercias = []
    silhuetas = []
    K = range(2, min(max_k + 1, len(X_scaled)))

    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inercias.append(kmeans.inertia_)
        silhuetas.append(silhouette_score(X_scaled, kmeans.labels_))

    # Encontrar cotovelo (maior redução relativa)
    reducoes = []
    for i in range(1, len(inercias)):
        reducao = (inercias[i-1] - inercias[i]) / inercias[i-1]
        reducoes.append(reducao)

    # Número ideal baseado em silhueta e redução de inércia
    idx_ideal = np.argmax(silhuetas)
    n_clusters_ideal = list(K)[idx_ideal]

    return n_clusters_ideal, inercias, silhuetas


def treinar_clustering(X_scaled, n_clusters):
    """Treina modelo de clustering K-means."""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    return kmeans


def analisar_clusters(kmeans, features_equipe, X_scaled):
    """Analisa características de cada cluster."""
    features_equipe['cluster'] = kmeans.labels_

    # Análise por cluster
    analise_clusters = features_equipe.groupby('cluster').agg({
        'pontos_auto': 'mean',
        'pontos_tele': 'mean',
        'total_pecas': 'mean',
        'links': 'mean',
        'vitoria': 'mean',
        'equipe': 'count'
    }).round(2)

    analise_clusters.rename(columns={'equipe': 'num_equipes'}, inplace=True)

    # Nomear clusters baseado em características
    nomes_clusters = []
    for idx, row in analise_clusters.iterrows():
        if row['vitoria'] > 0.7 and row['total_pecas'] > analise_clusters['total_pecas'].mean():
            nome = "Elite"
        elif row['pontos_auto'] > analise_clusters['pontos_auto'].mean() * 1.2:
            nome = "Especialista Autônomo"
        elif row['pontos_tele'] > analise_clusters['pontos_tele'].mean() * 1.2:
            nome = "Especialista Teleoperado"
        elif row['links'] > analise_clusters['links'].mean() * 1.5:
            nome = "Estrategista de Links"
        elif row['vitoria'] < 0.3:
            nome = "Em Desenvolvimento"
        else:
            nome = "Equilibrado"

        nomes_clusters.append(nome)

    analise_clusters['tipo_equipe'] = nomes_clusters

    return analise_clusters, features_equipe


def preparar_features_classificacao(dados):
    """Prepara features para classificação de vitória/derrota."""
    features = [
        'pontos_auto', 'pontos_tele', 'total_pecas_auto',
        'total_pecas_tele', 'links', 'penalidades_oponente'
    ]

    # Criar features binárias para charge station
    dados['teve_auto_charge'] = dados['auto_charge_station'].isin(['Engajado', 'Docked']).astype(int)
    dados['teve_tele_charge'] = dados['tele_charge_station'].isin(['Engajado', 'Docked']).astype(int)

    features.extend(['teve_auto_charge', 'teve_tele_charge'])

    # Criar feature de proporção de ROWs
    dados['prop_row_alta'] = (
        (dados['auto_row_topo'] + dados['tele_row_topo']) /
        (dados['total_pecas'] + 0.001)  # Evitar divisão por zero
    )
    features.append('prop_row_alta')

    X = dados[features].fillna(0)
    y = dados['vitoria']

    return X, y, features


def treinar_classificador(X, y):
    """Treina Random Forest para prever vitórias."""
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Treinar modelo
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )

    rf.fit(X_train, y_train)

    # Avaliar modelo
    y_pred = rf.predict(X_test)
    relatorio = classification_report(y_test, y_pred, output_dict=True)

    # Importância das features
    importancias = pd.DataFrame({
        'feature': X.columns,
        'importancia': rf.feature_importances_
    }).sort_values('importancia', ascending=False)

    return rf, relatorio, importancias, (X_test, y_test)


def gerar_insights_modelo(analise_clusters, importancias, relatorio):
    """Gera insights dos modelos para o relatório."""
    insights = {}

    # Insights de Clustering
    cluster_elite = analise_clusters[analise_clusters['tipo_equipe'] == 'Elite']
    if not cluster_elite.empty:
        insights['ClusterElite'] = (
            f"{int(cluster_elite['num_equipes'].sum())} equipes | "
            f"Taxa vitória: {cluster_elite['vitoria'].mean():.1%}"
        )

    insights['TotalClustersIdentificados'] = len(analise_clusters)

    cluster_maior = analise_clusters.loc[analise_clusters['num_equipes'].idxmax()]
    insights['ClusterMaisComum'] = (
        f"{cluster_maior['tipo_equipe']} ({int(cluster_maior['num_equipes'])} equipes)"
    )

    # Insights de Classificação
    insights['AcuraciaPrevisaoVitoria'] = f"{relatorio['accuracy']:.1%}"

    top_features = importancias.head(3)
    features_importantes = []
    for _, row in top_features.iterrows():
        feature_nome = row['feature'].replace('_', ' ').title()
        features_importantes.append(f"{feature_nome} ({row['importancia']:.1%})")

    insights['FatoresMaisImportantesVitoria'] = " | ".join(features_importantes)

    # Análise específica de features
    if 'penalidades_oponente' in importancias['feature'].values:
        imp_penalidade = importancias[importancias['feature'] == 'penalidades_oponente']['importancia'].values[0]
        insights['ImportanciaPenalidades'] = f"{imp_penalidade:.1%}"

    return insights


def executar_pipeline_completo(dados):
    """Executa todo o pipeline de treinamento de modelos."""
    resultados = {}

    # Clustering
    X_scaled, features_equipe, scaler = preparar_features_clustering(dados)
    n_clusters_ideal, inercias, silhuetas = encontrar_numero_clusters_ideal(X_scaled)
    kmeans = treinar_clustering(X_scaled, n_clusters_ideal)
    analise_clusters, features_equipe_cluster = analisar_clusters(kmeans, features_equipe, X_scaled)

    # Classificação
    X, y, feature_names = preparar_features_classificacao(dados)
    rf, relatorio, importancias, (X_test, y_test) = treinar_classificador(X, y)

    # Gerar insights
    insights = gerar_insights_modelo(analise_clusters, importancias, relatorio)

    # Compilar resultados
    resultados['modelos'] = {
        'kmeans': kmeans,
        'random_forest': rf,
        'scaler': scaler
    }

    resultados['analises'] = {
        'clusters': analise_clusters,
        'equipes_cluster': features_equipe_cluster,
        'importancia_features': importancias,
        'relatorio_classificacao': relatorio
    }

    resultados['insights'] = insights

    return resultados
