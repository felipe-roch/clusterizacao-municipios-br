import streamlit as st
import pandas as pd
import geopandas as gpd
import geobr
import plotly.express as px
from pathlib import Path
import json
import base64

def img_para_base64(caminho):
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_fundo = img_para_base64(Path(__file__).parent / 'imagens' / 'fundo.png')

st.set_page_config(page_title='Clusterização de Municípios Brasileiros', layout='wide')

st.markdown(f"""
<style>
.block-container {{
    padding-top: 1rem;
    padding-right: 1rem;
    padding-left: 1rem;
}}
[data-testid="stMainBlockContainer"] {{
    background-image: url("data:image/png;base64,{img_fundo}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
[data-testid="stHeader"] {{
    background-color: rgba(0, 0, 0, 0) !important;
}}
</style>
""", unsafe_allow_html=True)

st.title('Clusterização de Municípios Brasileiros por Perfil Socioeconômico')

cores = {
    'Desenvolvido': '#2ca02c',
    'Rural de Média Renda': '#9467bd',
    'Em Transição': '#ff7f0e',
    'Em Desenvolvimento': '#1f77b4',
    'Crítico': '#d62728',
    'Sem dados': '#cccccc'
}

regioes_ufs = {
    'Norte': ['AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MS', 'MT'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC']
}

@st.cache_data
def carregar_dados():
    caminho = Path(__file__).parent / 'dados' / 'processados'
    dados = pd.read_csv(caminho / 'dados_final.csv')
    mapa = geobr.read_municipality(code_muni="all", year=2020)
    mapa['code_muni'] = mapa['code_muni'].astype(int)

    colunas_merge = [
        'cod_municipio', 'cluster_nome', 'uf',
        'perc_agua_rede', 'perc_esgoto_rede', 'perc_lixo_coletado',
        'perc_alfabetizacao', 'renda_media', 'per_domicilio_urbano',
        'IDHM', 'IDHM Renda', 'IDHM Educação', 'IDHM Longevidade'
    ]
    mapa_final = mapa.merge(dados[colunas_merge],
                            left_on='code_muni',
                            right_on='cod_municipio',
                            how='left')
    mapa_final['cluster_nome'] = mapa_final['cluster_nome'].fillna('Sem dados')
    mapa_final['geometry'] = mapa_final['geometry'].simplify(0.005)
    return dados, mapa_final

dados, mapa_final = carregar_dados()

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.header('Filtros')

cluster_opcoes = ['Todos'] + sorted(dados['cluster_nome'].dropna().unique().tolist())
cluster_selecionado = st.sidebar.selectbox('Cluster:', options=cluster_opcoes)

regioes_opcoes = sorted(regioes_ufs.keys())
regioes_selecionadas = st.sidebar.multiselect('Regiões:', options=regioes_opcoes, default=regioes_opcoes)
if not regioes_selecionadas:
    regioes_selecionadas = regioes_opcoes

ufs_das_regioes = [uf for r in regioes_selecionadas for uf in regioes_ufs[r]]
uf_opcoes = sorted(dados[dados['uf'].isin(ufs_das_regioes)]['uf'].dropna().unique().tolist())
ufs_selecionadas = st.sidebar.multiselect('Estados (UF):', options=uf_opcoes, default=uf_opcoes)
if not ufs_selecionadas:
    ufs_selecionadas = uf_opcoes

# Filtro de municípios — lista já limitada às UFs selecionadas
municipios_opcoes = sorted(dados[dados['uf'].isin(ufs_selecionadas)]['municipio'].dropna().unique().tolist())
municipios_selecionados = st.sidebar.multiselect(
    'Municípios:',
    options=municipios_opcoes,
    placeholder='Digite o nome do município...'
)

st.sidebar.markdown("---")
st.sidebar.header('Filtros de Indicadores')

def slider_sidebar(label, coluna):
    vmin = float(dados[coluna].min())
    vmax = float(dados[coluna].max())
    return st.sidebar.slider(label, vmin, vmax, (vmin, vmax), step=0.1)

range_agua    = slider_sidebar('💧 Água (%)',        'perc_agua_rede')
range_esgoto  = slider_sidebar('🚿 Esgoto (%)',      'perc_esgoto_rede')
range_lixo    = slider_sidebar('🗑️ Lixo (%)',       'perc_lixo_coletado')
range_alfab   = slider_sidebar('📚 Alfabetiz. (%)', 'perc_alfabetizacao')
range_renda   = slider_sidebar('💰 Renda (R$)',      'renda_media')
range_urb     = slider_sidebar('🏙️ Urbaniz. (%)',   'per_domicilio_urbano')
range_idhm    = slider_sidebar('📊 IDHM',           'IDHM')
range_idhm_r  = slider_sidebar('💵 IDHM Renda',     'IDHM Renda')
range_idhm_ed = slider_sidebar('🎓 IDHM Educ.',     'IDHM Educação')
range_idhm_lo = slider_sidebar('❤️ IDHM Longevid.', 'IDHM Longevidade')

# ── Filtragem ─────────────────────────────────────────────
dados_filtrados = dados[dados['uf'].isin(ufs_selecionadas)]
if cluster_selecionado != 'Todos':
    dados_filtrados = dados_filtrados[dados_filtrados['cluster_nome'] == cluster_selecionado]

dados_filtrados = dados_filtrados[
    dados_filtrados['perc_agua_rede'].between(*range_agua) &
    dados_filtrados['perc_esgoto_rede'].between(*range_esgoto) &
    dados_filtrados['perc_lixo_coletado'].between(*range_lixo) &
    dados_filtrados['perc_alfabetizacao'].between(*range_alfab) &
    dados_filtrados['renda_media'].between(*range_renda) &
    dados_filtrados['per_domicilio_urbano'].between(*range_urb) &
    dados_filtrados['IDHM'].between(*range_idhm) &
    dados_filtrados['IDHM Renda'].between(*range_idhm_r) &
    dados_filtrados['IDHM Educação'].between(*range_idhm_ed) &
    dados_filtrados['IDHM Longevidade'].between(*range_idhm_lo)
]

# Sincroniza mapa com municípios filtrados pelos sliders
cods_filtrados = set(dados_filtrados['cod_municipio'])
mapa_filtrado = mapa_final[
    mapa_final['uf'].isin(ufs_selecionadas) &
    mapa_final['cod_municipio'].isin(cods_filtrados)
]
if cluster_selecionado != 'Todos':
    mapa_filtrado = mapa_filtrado[mapa_filtrado['cluster_nome'] == cluster_selecionado]

# Aplica filtro de municípios específicos (após todos os outros)
if municipios_selecionados:
    dados_filtrados = dados_filtrados[dados_filtrados['municipio'].isin(municipios_selecionados)]
    cods_filtrados = set(dados_filtrados['cod_municipio'])
    mapa_filtrado = mapa_filtrado[mapa_filtrado['cod_municipio'].isin(cods_filtrados)]

# ── Função KPI ────────────────────────────────────────────
def kpi2(col, titulo, valor_medio, valor_max, valor_min, formato='%'):
    if formato == 'R$':
        v_med = f"R$ {valor_medio:.0f}"
        v_max = f"R$ {valor_max:.0f}"
        v_min = f"R$ {valor_min:.0f}"
    elif formato == 'idx':
        v_med = f"{valor_medio:.3f}"
        v_max = f"{valor_max:.3f}"
        v_min = f"{valor_min:.3f}"
    else:
        v_med = f"{valor_medio:.1f}%"
        v_max = f"{valor_max:.1f}%"
        v_min = f"{valor_min:.1f}%"
    with col:
        st.markdown(f"""
        <div style="background:#f9f9f9; border:1px solid #e0e0e0; border-radius:10px; padding:8px 6px; margin-bottom:8px;">
            <div style="font-size:11px; color:#666; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{titulo}</div>
            <div style="font-size:17px; font-weight:bold;">{v_med}</div>
            <div style="font-size:10px; color:#888;">▲ {v_max}</div>
            <div style="font-size:10px; color:#888;">▼ {v_min}</div>
        </div>
        """, unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6,k7,k8,k9,k10 = st.columns(10)

kpi2(k1,  '💧 Água',      dados_filtrados['perc_agua_rede'].mean(),       dados_filtrados['perc_agua_rede'].max(),       dados_filtrados['perc_agua_rede'].min())
kpi2(k2,  '🚿 Esgoto',    dados_filtrados['perc_esgoto_rede'].mean(),     dados_filtrados['perc_esgoto_rede'].max(),     dados_filtrados['perc_esgoto_rede'].min())
kpi2(k3,  '🗑️ Lixo',     dados_filtrados['perc_lixo_coletado'].mean(),   dados_filtrados['perc_lixo_coletado'].max(),   dados_filtrados['perc_lixo_coletado'].min())
kpi2(k4,  '📚 Alfab.',    dados_filtrados['perc_alfabetizacao'].mean(),   dados_filtrados['perc_alfabetizacao'].max(),   dados_filtrados['perc_alfabetizacao'].min())
kpi2(k5,  '💰 Renda',     dados_filtrados['renda_media'].mean(),          dados_filtrados['renda_media'].max(),          dados_filtrados['renda_media'].min(), 'R$')
kpi2(k6,  '🏙️ Urb.',     dados_filtrados['per_domicilio_urbano'].mean(), dados_filtrados['per_domicilio_urbano'].max(), dados_filtrados['per_domicilio_urbano'].min())
kpi2(k7,  '📊 IDHM',      dados_filtrados['IDHM'].mean(),                dados_filtrados['IDHM'].max(),                dados_filtrados['IDHM'].min(), 'idx')
kpi2(k8,  '💵 IDHM R.',   dados_filtrados['IDHM Renda'].mean(),          dados_filtrados['IDHM Renda'].max(),          dados_filtrados['IDHM Renda'].min(), 'idx')
kpi2(k9,  '🎓 IDHM Ed.',  dados_filtrados['IDHM Educação'].mean(),       dados_filtrados['IDHM Educação'].max(),       dados_filtrados['IDHM Educação'].min(), 'idx')
kpi2(k10, '❤️ IDHM Lo.',  dados_filtrados['IDHM Longevidade'].mean(),    dados_filtrados['IDHM Longevidade'].max(),    dados_filtrados['IDHM Longevidade'].min(), 'idx')

# ── Mapa ──────────────────────────────────────────────────
st.subheader('Mapa de Clusters')

cores_sem_dados = {k: v for k, v in cores.items() if k != 'Sem dados'}
cols_leg = st.columns(len(cores_sem_dados))
for i, (nome, cor) in enumerate(cores_sem_dados.items()):
    cols_leg[i].markdown(
        f'<span style="display:inline-block;width:12px;height:12px;background:{cor};'
        f'border-radius:2px;margin-right:5px;"></span>**{nome}**',
        unsafe_allow_html=True
    )

mapa_plot = mapa_filtrado.reset_index(drop=True)
geojson = json.loads(mapa_plot.to_json())
fig = px.choropleth(
    mapa_plot,
    geojson=geojson,
    locations=mapa_plot.index,
    color='cluster_nome',
    color_discrete_map=cores,
    hover_name='name_muni',
    hover_data={
        'uf': True,
        'cluster_nome': True,
        'perc_agua_rede': ':.2f',
        'perc_esgoto_rede': ':.2f',
        'perc_lixo_coletado': ':.2f',
        'perc_alfabetizacao': ':.2f',
        'renda_media': ':.0f',
        'per_domicilio_urbano': ':.2f',
        'IDHM': ':.3f',
        'IDHM Renda': ':.3f',
        'IDHM Educação': ':.3f',
        'IDHM Longevidade': ':.3f',
    },
    labels={
        'uf': 'UF',
        'cluster_nome': 'Cluster',
        'perc_agua_rede': 'Água (%)',
        'perc_esgoto_rede': 'Esgoto (%)',
        'perc_lixo_coletado': 'Lixo coletado (%)',
        'perc_alfabetizacao': 'Alfabetização (%)',
        'renda_media': 'Renda média (R$)',
        'per_domicilio_urbano': 'Urbanização (%)',
        'IDHM': 'IDHM',
        'IDHM Renda': 'IDHM Renda',
        'IDHM Educação': 'IDHM Educação',
        'IDHM Longevidade': 'IDHM Longevidade',
    },
    fitbounds='locations',
    basemap_visible=False,
)
fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    showlegend=False,
    height=650
)
st.plotly_chart(fig, use_container_width=True)