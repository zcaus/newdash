import streamlit as st
import pandas as pd
from datetime import datetime

# Define o layout da página como wide (tela inteira)
st.set_page_config(
    page_title="Sistema de Controle - Flash",
    page_icon="planilha/mascote_instagram-removebg-preview.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)


col1, col2 ,col3, col4, col5, col6, col7, col8 = st.columns(8)

with col1:
        st.page_link("main.py", label="Dashboard", icon="📊")
with col2:
        st.page_link("pages/carteira.py", label="Carteira", icon="📇")
with col3:
        st.page_link("pages/separacao.py", label="Separação", icon="💻")
with col4:
        st.page_link("pages/compras.py", label="Compras", icon="🛒")
with col5:
        st.page_link("pages/embalagem.py", label="Embalagem", icon="📦")
with col6:
        st.page_link("pages/expedicao.py", label="Expedição", icon="🚚")
with col7:
        st.page_link("pages/semOE.py", label="Sem OE", icon="❌")
with col8:
        st.page_link("pages/flash.py", label="Flash", icon="📅")

@st.cache_data
def carregar_dados():
    df = pd.read_excel('planilha/controledosistema.xlsx')
    return df

# Carrega os dados
df = carregar_dados()

exclusoes = [
    'TUMELERO', 'ESTOQUE FOX', 'TELHA 14.10.24', 'TELHA 18.10.24', 
    'FANAN/TERUYA', 'HC FOX 11.11.24', 'TUMELEIRO 2', 
    'AMOSTRAS', 'LOJAS 20.12.2024', 'SALDO TELHANORTE', "DISPLAY MB", "ESTOQUE 24.02", "ESTOQUE 17.02"
]

df = df[~df['Ped. Cliente'].isin(exclusoes)]

# Converte a coluna de data do pedido para datetime, tratando erros
df['Dt.pedido'] = pd.to_datetime(
    df['Dt.pedido'], dayfirst=True, errors='coerce', infer_datetime_format=True
)

# Remove linhas sem data válida em Dt.pedido
df = df.dropna(subset=['Dt.pedido'])

# Cria uma nova coluna com o formato Ano-Mês (ex.: "2025-02")
df['Mes/Ano'] = df['Dt.pedido'].dt.strftime('%Y-%m')

# Cria um filtro para selecionar o mês desejado
meses = sorted(df['Mes/Ano'].unique())

# Define o mês atual e verifica se ele está presente na lista de meses
mes_atual = datetime.today().strftime('%Y-%m')
default_index = meses.index(mes_atual) if mes_atual in meses else 0

mes_selecionado = st.selectbox("Selecione o mês", meses, index=default_index)

# Filtra os pedidos do mês selecionado
df_mes = df[df['Mes/Ano'] == mes_selecionado]

# Agrupa os pedidos de forma unificada:
# Para cada Fantasia, Ped. Cliente (número do pedido) e Dt.pedido, soma o Valor Total
pedidos_agrupados = df_mes.groupby(
    ['Fantasia', 'Ped. Cliente', 'Dt.pedido'], as_index=False
)['Valor Total'].sum()

# Renomeia as colunas para melhor visualização
pedidos_agrupados.rename(columns={
    'Fantasia': 'Fantasia',
    'Ped. Cliente': 'Ped. Cliente',
    'Dt.pedido': 'Data do Pedido',
    'Valor Total': 'Valor Total do Pedido'
}, inplace=True)

# Calcula o total de todos os pedidos do mês
total_mes = pedidos_agrupados['Valor Total do Pedido'].sum()

# Meta fixa definida
meta_mes = 843150.00

# Calcula o percentual da meta batida
percentual = (total_mes / meta_mes) * 100 if meta_mes > 0 else 0

# Calcula quanto falta em R$ para bater a meta (se já batida, mostra 0)
falta_valor = meta_mes - total_mes if total_mes < meta_mes else 0

# Cria cinco colunas para exibir as informações no topo da página
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Valor Total dos Pedidos", f"R$ {total_mes:,.2f}")
col2.metric("Meta do Mês", f"R$ {meta_mes:,.2f}")
if percentual < 100:
    col3.metric("Falta para Meta (%)", f"{100 - percentual:.2f}%")
else:
    col3.metric("Falta para Meta (%)", "0%")
col4.metric("Meta Batida (%)", f"{percentual:.2f}%")
col5.metric("Falta para Meta (R$)", f"R$ {falta_valor:,.2f}")

st.header(f"Flash de Vendas do Mês {mes_selecionado}")

# Exibe os pedidos unificados com a coluna Fantasia e Ped. Cliente em tela inteira
st.dataframe(pedidos_agrupados, use_container_width=True)
