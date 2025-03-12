import streamlit as st
import pandas as pd
from datetime import datetime

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

# Navegação
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
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

df = carregar_dados()

# Limpa nomes de colunas
df.columns = df.columns.str.strip()

# Diagnóstico das colunas
st.write("Colunas do df original:", df.columns.tolist())

# Lista de exclusões
exclusoes = [
    'TUMELERO', 'ESTOQUE FOX', 'TELHA 14.10.24', 'TELHA 18.10.24', 
    'FANAN/TERUYA', 'HC FOX 11.11.24', 'TUMELEIRO 2', 
    'AMOSTRAS', 'LOJAS 20.12.2024', 'SALDO TELHANORTE', 
    "DISPLAY MB", "ESTOQUE 24.02", "ESTOQUE 17.02"
]

df = df[~df['Ped. Cliente'].isin(exclusoes)]

df['Dt.pedido'] = pd.to_datetime(
    df['Dt.pedido'], dayfirst=True, errors='coerce', infer_datetime_format=True
)

df = df.dropna(subset=['Dt.pedido'])

df['Mes/Ano'] = df['Dt.pedido'].dt.strftime('%Y-%m')

meses = sorted(df['Mes/Ano'].unique())

mes_atual = datetime.today().strftime('%Y-%m')
default_index = meses.index(mes_atual) if mes_atual in meses else 0

mes_selecionado = st.selectbox("Selecione o mês", meses, index=default_index)

df_mes = df[df['Mes/Ano'] == mes_selecionado]

# Diagnóstico das colunas depois do filtro
st.write("Colunas de df_mes:", df_mes.columns.tolist())

# Exibe os primeiros dados para inspecionar o conteúdo
st.dataframe(df_mes.head(10))

# Garante que não tem valores nulos no vendedor
if 'Vendedor' in df_mes.columns:
    df_mes['Vendedor'] = df_mes['Vendedor'].fillna('SEM VENDEDOR')
else:
    st.error("A coluna 'Vendedor' não existe no DataFrame após o filtro!")

# Agrupa
pedidos_agrupados = df_mes.groupby(
    ['Fantasia', 'Ped. Cliente', 'Dt.pedido', 'Vendedor'], as_index=False
)['Valor Total'].sum()

pedidos_agrupados.rename(columns={
    'Fantasia': 'Fantasia',
    'Ped. Cliente': 'Ped. Cliente',
    'Dt.pedido': 'Data do Pedido',
    'Vendedor': 'Vendedor',
    'Valor Total': 'Valor Total do Pedido'
}, inplace=True)

colunas_exibicao = ['Fantasia', 'Ped. Cliente', 'Vendedor', 'Data do Pedido', 'Valor Total do Pedido']

total_mes = pedidos_agrupados['Valor Total do Pedido'].sum()

meta_mes = 843150.00

percentual = (total_mes / meta_mes) * 100 if meta_mes > 0 else 0

falta_valor = meta_mes - total_mes if total_mes < meta_mes else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Valor Total dos Pedidos", f"R$ {total_mes:,.2f}")
col2.metric("Meta do Mês", f"R$ {meta_mes:,.2f}")
col3.metric("Falta para Meta (%)", f"{100 - percentual:.2f}%" if percentual < 100 else "0%")
col4.metric("Meta Batida (%)", f"{percentual:.2f}%")
col5.metric("Falta para Meta (R$)", f"R$ {falta_valor:,.2f}")

st.header(f"Flash de Vendas do Mês {mes_selecionado}")

st.dataframe(pedidos_agrupados[colunas_exibicao], use_container_width=True)
