# Clusterização de Municípios Brasileiros por Perfil Socioeconômico

## Descrição

Projeto de machine learning com o objetivo de analisar de maneira mais minuciosa e agrupar por perfis semelhantes os municípios brasileiros. Para tal, foram cruzados os dados do Atlas Brasil (PNUD/ONU), que leva em consideração o IDH desses municípios em algumas esferas, e de algumas pesquisas do Censo Demográfico de 2022 para encontrar municípios com características semelhantes entre si. Foram encontrados 5 clusters, que definem diferentes padrões de maturidade:
- Desenvolvido;
- Rurais com Média Renda;
- Em Transição;
- Em Desenvolvimento;
- Críticos.
Alguns padrões interessantes foram encontrados, viabilizando análises sobre desigualdade regional, com destaque para o cluster de Municípios Rurais de Média Renda, que apresenta renda elevada mas baixos índices de saneamento — padrão associado a municípios do agronegócio no Centro-Oeste e Sul do Brasil.

## Dados Utilizados

| Fonte | Tabela | Descrição | Ano |
|-------|--------|-----------|-----|
| Atlas Brasil - PNUD ONU | Ranking de IDH por Municípios | Índice de Desenvolvimento Humano Municipal (IDHM) e subíndices de Renda, Educação e Longevidade por município, baseado no Censo 2010. |2010|
| Sidra IBGE - Censo Demográfico (2022) | Tabela 6803 | Características dos Domicílios - Existência de ligação à rede geral de distribuição de água e principal forma de abastecimento de água |2022|
| Sidra IBGE - Censo Demográfico (2022) | Tabela 6805 | Características dos Domicílios - Domicílios particulares permanentes ocupados, por tipo de esgotamento sanitário |2022|
| Sidra IBGE - Censo Demográfico (2022) | Tabela 6892 | Características dos Domicílios - Domicílios particulares permanentes ocupados, por destino do lixo |2022|
| Sidra IBGE - Censo Demográfico (2022) | Tabela 9543 | Alfabetização - Taxa de alfabetização das pessoas de 15 anos ou mais de idade por sexo, cor ou raça e grupos de idade |2022|
| Sidra IBGE - Censo Demográfico (2022) | Tabela 10295 | Trabalho e Rendimento - Moradores em domicílios particulares permanentes ocupados, exclusive os cuja condição no domicílio era pensionista, empregado(a) doméstico(a) ou parente do(a) empregado(a) doméstico(a), valor do rendimento domiciliar mensal per capita, médio e mediano, por sexo, cor ou raça e grupos de idade |2022|
| Sidra IBGE - Censo Demográfico (2022) | Tabela 9923 | População e Domicílios por situação urbana ou rural do domicílio - População residente, por situação do domicílio |2022|

## Metodologia

1. Coleta de dados via API SIDRA (sidrapy) e Atlas Brasil
2. Tratamento e padronização dos nomes de municípios entre as bases
3. Merge das bases por código IBGE
4. Tratamento de valores nulos com mediana por UF
5. Normalização com StandardScaler
6. Definição do número de clusters via Método do Cotovelo e Silhouette Score
7. Clustering com K-Means (k=5)
8. Visualização geoespacial com GeoBR e GeoPandas

## Estrutura do Projeto

Clusterizacao_Municipios/
├── dados/
│   ├── brutos/                    ← Atlas_BR_Municipios.xlsx
│   └── processados/               ← Atlas_tratado.csv, sidra_consolidado.csv, dados_final.csv
├── imagens/                       ← Gráficos gerados pelo notebook 04
│   ├── cotovelo.png
│   ├── silhouette.png
│   ├── mapa_clusters.png
│   └── radar_clusters.png
└── notebooks/
    ├── 01_coleta.ipynb            ← Carregamento e tratamento do Atlas Brasil
    ├── 02_sidra.ipynb             ← Coleta e tratamento dos dados via API SIDRA
    ├── 03_preprocessamento.ipynb  ← Merge das bases e tratamento de nulos
    └── 04_clusterizacao.ipynb     ← Modelagem K-Means, visualizações e resultados

Para melhor organização das etapas de execução do projeto, optou-se por dividir em duas pastas principais, "dados", onde se concentram os dados a serem utilizados nas análises e concentra as subpastas "brutos" e processados", e "notebooks", para centralizar a execução e as etapas do projeto. A subpasta "brutos" é o local em que foi armazenado o arquivo .csv extraído do Atlas Brasil, das Nações Unidas. Na subpasta "processados" temos três arquivos, "Atlas_tratado.csv", "sidra_consolidado.csv" e "dados_final.csv", que foram gerados após os tratamentos realizados pelos notebooks.
Na pasta "notebooks" estão os cadernos: "01_coleta.ipynb", "02_sidra.ipynb", "03_preprocessamento.ipynb" e "04_clusteracao.ipynb". Os dois primeiros foram destinados a coleta e tratamento dos dados a serem utilizados posteriormente, no primeiro essencialmente houve o tratamento do .csv do Atlas e deposição na pasta "processados". Já no segundo, estão contidas as extrações realizadas pela API e junção para posterior envio do arquivo para a pasta "processados". No arquivo 03, foi realizada a normalização dos dados e junção das duas fontes de dados, dando preferência aos dados do Sidra (2022), por serem mais recentes que os dados do Atlas Brasil (2010), entendendo que nele estariam as mudanças mais novas ocorridas na geografia dos municípios brasileiros. Por fim, no notebook 04, temos finalmente a aplicação do modelo de machine learning (K-Means) e segmentação dos municípios em cinco clusters.

## Resultados
### Clusters identificados

| Cluster | Nº de Municípios | Perfil |
|---------|------------------|--------|
| Municípios Desenvolvidos | 1425 | Maior saneamento, maior alfabetização, maior urbanização (89%), IDHM alto (0.74) |
| Municípios Rurais de Média Renda | 819 | Renda alta (1704) mas baixo saneamento (14%), baixa urbanização (53%) |
| Municípios em Transição | 1195 | Perfil intermediário equilibrado|
| Municípios em Desenvolvimento | 1242 | Valores intermediários em tudo, menor IDHM Educação (0.49) |
| Municípios Críticos | 884 | Menor renda (712), menor saneamento, menor urbanização (44%), menor IDHM (0.56) |
* Clusters ordenados de acordo com valores de IDHM.

### Visualizações

**Mapa de Clusters por Município**
![Mapa de Clusters](imagens/mapa_clusters.png)

**Perfil Médio dos Clusters**
![Radar dos Clusters](imagens/radar_clusters.png)

**Definição do número de clusters**
![Cotovelo e Silhouette](imagens/cotovelo.png)

## Como Executar
### Requisitos

Python 3.9+

pip install pandas sidrapy geopandas geobr scikit-learn matplotlib requests openpyxl

### Ordem de execução

Os cadernos devem ser executados sequencialmente, do 1° ao 4°, para que os dados sejam coletados, tratados, consolidados e a segmentação por ML seja realizada com sucesso.

## Tecnologias Utilizadas

- Python 3.13.9 (Anaconda)
- pandas, numpy
- sidrapy, requests
- scikit-learn
- matplotlib, geopandas, geobr

## Autor

Felipe da Rocha
[Linkedin](https://www.linkedin.com/in/felipedarochaferreira/) · [GitHub](http://github.com/felipe-roch)