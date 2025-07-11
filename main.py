import streamlit as st
import pandas as pd
from datetime import datetime
import locale
import plotly.express as px
from io import BytesIO
import plotly.graph_objects as go
from streamlit.components.v1 import html
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sistema de Controle",
    page_icon="images/mascote_instagram-removebg-preview.png",
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

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')

current_date = datetime.now()

@st.cache_data
def carregar_dados():
    df = pd.read_excel('planilha/controledosistema.xlsx')
    return df

df = carregar_dados()

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

dados = st.session_state.dados

df['Nr.pedido'] = df['Nr.pedido'].astype(str)

separacao = df[~df['Nr.pedido'].str.contains('-')]
perfil2 = df[df['Nr.pedido'].str.contains('-')]

perfil3 = perfil2[perfil2['Origem'].isna() | (perfil2['Origem'] == '')]

perfil2 = perfil2[~perfil2.index.isin(perfil3.index)]

def definir_data_e_status(dataframe):

    dataframe['Dt.fat.'] = pd.to_datetime(dataframe['Dt.fat.'], errors='coerce')
    dataframe['Prev.entrega'] = pd.to_datetime(dataframe['Prev.entrega'], errors='coerce')

    dataframe['Status'] = 'Pendente'
    dataframe.loc[dataframe['Dt.fat.'].notna(), 'Status'] = 'Entregue'
    dataframe.loc[(dataframe['Prev.entrega'] < datetime.now()) & (dataframe['Dt.fat.'].isna()), 'Status'] = 'Atrasado'
    
    return dataframe

carteira = df

def is_atrasado_pedido(df):
    return (df['Dt.pedido'] + pd.Timedelta(days=1)) < datetime.now()

colunas_desejadas = [
     'Setor', 'Ped. Cliente', 'Dt.pedido', 'Fantasia', 'Produto', 'Modelo', 
    'Qtd.', 'Valor Unit.', 'Valor Total', 'Qtd.a produzir', 
    'Qtd. Produzida', 'Qtd.a liberar','Prev.entrega','Dt.fat.' , 'Nr.pedido'
]

st.markdown("""
    <style>
    body {
        color: white; /* Cor do texto */
    }
    .stApp {
    }
    .styled-col {
        border: 2px solid #094780;
        background-color:rgba(9, 70, 128, 0.39);
        border-radius: 10px;
        padding: 5px; /* Reduzido para diminuir o espaço */
        margin: 5px; /* Reduzido para diminuir o espaço */
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 70px; /* Altura mínima para todas as colunas */
        font-size: 1em; /* Tamanho da fonte ajustado */
        box-shadow: inset -30px -30px 45px rgba(0, 0, 0, 0.2);
    }
    .metric-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    .metric-label {
        font-size: 1em; /* Tamanho da fonte ajustado */
        font-weight: bold;
        margin-bottom: 5px; /* Espaço entre o rótulo e o valor */
    }
    .metric-value {
        font-size: 2em; /* Tamanho da fonte ajustado */
        font-weight: bold;
    }
    .chart-container {
    background-color:242F4A;
    padding: 5px; /* Reduzido para diminuir o espaço */
    margin: 5px; /* Reduzido para diminuir o espaço */
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 150px; /* Altura mínima para todas as colunas */
    font-size: 0.9em; /* Tamanho da fonte ajustado */
    box-shadow: inset -30px -30px 45px rgba(0, 0, 0, 0.2);
    }
    .date-filters {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 1001;
        display: flex;
        flex-direction: column;
        gap: 5px;
        background-color: #094780;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

separacao = separacao[colunas_desejadas]
perfil2 = perfil2[colunas_desejadas]
compras = perfil2[(perfil2['Qtd. Produzida'] == 0) & (perfil2['Qtd.a liberar'] == 0)][colunas_desejadas]
embalagem = perfil2[(perfil2['Qtd. Produzida'] == 0) & (perfil2['Qtd.a liberar'] > 0)][colunas_desejadas]
expedicao = perfil2[(perfil2['Qtd. Produzida'] > 0) & (perfil2['Qtd.a liberar'] > 0)][colunas_desejadas]
perfil3 = perfil3[colunas_desejadas]
carteira = carteira[colunas_desejadas]

separacao = separacao.dropna(subset=['Ped. Cliente'])
perfil2 = perfil2.dropna(subset=['Ped. Cliente'])
compras = compras.dropna(subset=['Ped. Cliente'])
embalagem = embalagem.dropna(subset=['Ped. Cliente'])
expedicao = expedicao.dropna(subset=['Ped. Cliente'])
perfil3 = perfil3.dropna(subset=['Ped. Cliente'])
carteira = carteira.dropna(subset=['Ped. Cliente'])

separacao = definir_data_e_status(separacao)
perfil2 = definir_data_e_status(perfil2)
compras = definir_data_e_status(compras)
embalagem = definir_data_e_status(embalagem)
expedicao = definir_data_e_status(expedicao)
perfil3 = definir_data_e_status(perfil3)
carteira = definir_data_e_status(carteira)

separacao = separacao[(separacao['Ped. Cliente'] != 'LOJAS 11.04') & (separacao['Ped. Cliente'] != 'LOJAS 14.06') & (separacao['Ped. Cliente'] != 'LOJAS 23.05') & (separacao['Ped. Cliente'] != 'CUMBICA 6849') & (separacao['Ped. Cliente'] != 'AMOSTRA ROGER') & (separacao['Ped. Cliente'] != 'AMOSTRAS LITORA') & (separacao['Ped. Cliente'] != 'AMOSTRAS REINALDO') & (separacao['Ped. Cliente'] != '202543')]
compras = compras[(compras['Ped. Cliente'] != 'LOJAS 11.04') & (compras['Ped. Cliente'] != 'LOJAS 14.06') & (compras['Ped. Cliente'] != 'LOJAS 23.05') & (compras['Ped. Cliente'] != 'CUMBICA 6849') & (compras['Ped. Cliente'] != 'AMOSTRA ROGER') & (compras['Ped. Cliente'] != 'AMOSTRAS LITORA') & (compras['Ped. Cliente'] != 'AMOSTRAS REINALDO') & (compras['Ped. Cliente'] != '202543')]
embalagem = embalagem[(embalagem['Ped. Cliente'] != 'LOJAS 11.04') & (embalagem['Ped. Cliente'] != 'LOJAS 14.06') & (embalagem['Ped. Cliente'] != 'LOJAS 23.05') & (embalagem['Ped. Cliente'] != 'CUMBICA 6849') & (embalagem['Ped. Cliente'] != 'AMOSTRA ROGER') & (embalagem['Ped. Cliente'] != 'AMOSTRAS LITORA') & (embalagem['Ped. Cliente'] != 'AMOSTRAS REINALDO') & (embalagem['Ped. Cliente'] != '202543')]
expedicao = expedicao[(['Ped. Cliente'] != 'LOJAS 11.04') & (expedicao['Ped. Cliente'] != 'LOJAS 14.06') & (expedicao['Ped. Cliente'] != 'LOJAS 23.05') & (expedicao['Ped. Cliente'] != 'CUMBICA 6849') & (expedicao['Ped. Cliente'] != 'AMOSTRA ROGER') & (expedicao['Ped. Cliente'] != 'AMOSTRAS LITORA') & (expedicao['Ped. Cliente'] != 'AMOSTRAS REINALDO') & (expedicao['Ped. Cliente'] != '202543')]
perfil3 = perfil3[(perfil3['Ped. Cliente'] != 'LOJAS 11.04') & (perfil3['Ped. Cliente'] != 'LOJAS 14.06') & (perfil3['Ped. Cliente'] != 'LOJAS 23.05') & (perfil3['Ped. Cliente'] != 'CUMBICA 6849') & (perfil3['Ped. Cliente'] != 'AMOSTRA ROGER') & (perfil3['Ped. Cliente'] != 'AMOSTRAS LITORA') & (perfil3['Ped. Cliente'] != 'AMOSTRAS REINALDO') & (perfil3['Ped. Cliente'] != '202543')]
carteira = carteira[(carteira['Ped. Cliente'] != 'LOJAS 11.04') & (carteira['Ped. Cliente'] != 'LOJAS 14.06') & (carteira['Ped. Cliente'] != 'LOJAS 23.05') & (carteira['Ped. Cliente'] != 'CUMBICA 6849') & (carteira['Ped. Cliente'] != 'AMOSTRA ROGER') & (carteira['Ped. Cliente'] != 'AMOSTRAS LITORA') & (carteira['Ped. Cliente'] != 'AMOSTRAS REINALDO') & (carteira['Ped. Cliente'] != '202543')]

separacao = separacao[separacao['Nr.pedido']!= 'nan']
perfil2 = perfil2[perfil2['Nr.pedido']!= 'nan']
compras = compras[compras['Nr.pedido']!= 'nan']
embalagem = embalagem[embalagem['Nr.pedido']!= 'nan']
expedicao = expedicao[expedicao['Nr.pedido']!= 'nan']
perfil3 = perfil3[perfil3['Nr.pedido']!= 'nan']
carteira = carteira[carteira['Nr.pedido']!= 'nan']

separacao = separacao[separacao['Status']!= 'Entregue']
compras = compras[compras['Status']!= 'Entregue']
embalagem = embalagem[embalagem['Status']!= 'Entregue']
expedicao = expedicao[expedicao['Status']!= 'Entregue']
perfil3 = perfil3[perfil3['Status']!= 'Entregue']

def formatar_data(data):
    return data.strftime("%d/%m/%Y")

def guia_carteira():
    st.title("Carteira")
    
    df_filtrado = carteira
    df_carteira = carteira
    df_carteira = definir_data_e_status(df_carteira)

    col_filter1, col_filter2, col_filter3, col_filter4, col_date_filter1, col_date_filter2 = st.columns(6)
    
    with col_filter1:
        fantasia_filter = st.selectbox("Selecione o Cliente", options=["Todos"] + list(df_carteira['Fantasia'].unique()))
    
    with col_filter2:
        ped_cliente_filter = st.selectbox("Filtrar por Pedido", options=["Todos"] + list(df_carteira['Ped. Cliente'].unique()))
    
    with col_filter3:
        status_filter = st.selectbox("Filtrar por Status", options=["Todos", "Entregue", "Pendente", "Atrasado"])
    
    with col_filter4:
        setor_filter = st.selectbox("Filtrar por Setor", options=["Todos"] + [s for s in df_carteira['Setor'].unique() if not pd.isnull(s) and s!= 'Entregue'])

    with col_date_filter1:
        data_inicial_filter = pd.to_datetime(st.date_input("Data Inicial", value=pd.to_datetime('2025-04-01')))
    
    with col_date_filter2:
        data_final_filter = pd.to_datetime(st.date_input("Data Final", value=pd.to_datetime('today')))

    df_carteira_filtrado = df_carteira.copy()
    if fantasia_filter!= "Todos":
        df_carteira_filtrado = df_carteira_filtrado[df_carteira_filtrado['Fantasia'] == fantasia_filter]
    if ped_cliente_filter!= "Todos":
        df_carteira_filtrado = df_carteira_filtrado[df_carteira_filtrado['Ped. Cliente'] == ped_cliente_filter]
    if status_filter!= "Todos":
        df_carteira_filtrado = df_carteira_filtrado[df_carteira_filtrado['Status'] == status_filter]
    if setor_filter!= "Todos":
        df_carteira_filtrado= df_carteira_filtrado[df_carteira_filtrado['Setor'] == setor_filter] 
    
    if not df_carteira_filtrado.empty:
        st.write("Total de Itens:", len(df_carteira_filtrado))
        st.dataframe(df_carteira_filtrado)
        valor_total = f"R$ {df_carteira_filtrado['Valor Total'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(f"<span style='font-size: 20px;'><b>Valor Total:</b> {valor_total}</span>", unsafe_allow_html=True)
    else:
        st.warning("Nenhum item encontrado com os filtros aplicados.")  

    df_filtrado = df[colunas_desejadas]

    def gerar_excel(df):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatório')
        buffer.seek(0)
        return buffer

    excel_file = gerar_excel(df_filtrado)

    st.download_button(
        label="Exportar Relatório",
        data=excel_file,
        file_name="relatorio_dataframe.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def guia_dashboard():

    col1, col2 ,col3, col4, col5, col6, col7 = st.columns(7)

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

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        data_inicial_filter = st.date_input("Data Inicial", value=pd.to_datetime('2025-05-01').date())

    with col2:
        data_final_filter = st.date_input("Data Final", value=pd.to_datetime('today').date())

    df_filtrado = carteira[(carteira['Dt.pedido'].dt.date >= data_inicial_filter) & (carteira['Dt.pedido'].dt.date <= data_final_filter)]

    produto_frequencia = df_filtrado['Produto'].value_counts().reset_index()
    produto_frequencia.columns = ['Produto', 'Frequência']

    produto_info = df_filtrado[['Produto', 'Modelo']].drop_duplicates()

    produto_frequencia = produto_frequencia.merge(produto_info, on='Produto', how='left')

    total_pedidos = df_filtrado.loc[df_filtrado['Setor'] != 'Entregue', 'Ped. Cliente'].nunique()
    pendente = len(df_filtrado[df_filtrado['Status'] == 'Pendente'])
    atrasado = len(df_filtrado[df_filtrado['Status'] == 'Atrasado'])
    modelos_unicos = df_filtrado.loc[df_filtrado['Setor'] != 'Entregue', 'Produto'].nunique()
    total_itensct = df_filtrado.loc[df_filtrado['Setor'] != 'Entregue', 'Qtd.'].sum()

    valor_total_separacao = df_filtrado[df_filtrado['Setor'] == 'Separação']['Valor Total'].sum()
    valor_total_compras = df_filtrado[df_filtrado['Setor'] == 'Compras']['Valor Total'].sum()
    valor_total_embalagem = df_filtrado[df_filtrado['Setor'] == 'Embalagem']['Valor Total'].sum()
    valor_total_expedicao = df_filtrado[df_filtrado['Setor'] == 'Expedição']['Valor Total'].sum()

    valor_total_separacao_formatado = f"R${valor_total_separacao:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    valor_total_compras_formatado = f"R${valor_total_compras:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    valor_total_embalagem_formatado = f"R${valor_total_embalagem:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    valor_total_expedicao_formatado = f"R${valor_total_expedicao:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    col_esquerda, col_direita = st.columns(2)

    with col_esquerda:
        if data_inicial_filter.month == data_final_filter.month and data_inicial_filter.year == data_final_filter.year:
            mes_ano = data_inicial_filter.strftime('%m/%Y')
            periodo = f"{mes_ano}"
        else:
            mes_ano_inicial = data_inicial_filter.strftime('%m/%Y')
            mes_ano_final = data_final_filter.strftime('%m/%Y')
            periodo = f"{mes_ano_inicial} a {mes_ano_final}"

        st.markdown(f"""
            <div style='display: flex; align-items: center;'>
                <h1 style='margin-right: 5px; margin-bottom: 0;'>📊 Estatísticas Gerais</h1>
                <span style='font-size: 0.8em; color: gray; margin-bottom: 0;'>{periodo}</span>
            </div>
            """, unsafe_allow_html=True)

        sub_col1, sub_col2, sub_col3, sub_col4= st.columns([1,3,3,1])
        with sub_col2:
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Total de Pedidos</div>
                        <div class='metric-value'>{total_pedidos}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        #with sub_col2:
        #    st.markdown(f"""
        #        <div class='styled-col'>
        #            <div class='metric-container'>
        #                <div class='metric-label'>Total de Itens</div>
        #                <div class='metric-value'>{len(df)}</div>
        #            </div>
        #        </div>
        #        """, unsafe_allow_html=True)
        with sub_col3:
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Total de Pendências</div>
                        <div class='metric-value'>{pendente + atrasado}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        sub_col1, sub_col2, sub_col3, sub_col4= st.columns([1,3,3,1])
        
        with sub_col2:
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Total por Referência</div>
                        <div class='metric-value'>{modelos_unicos}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        with sub_col3:
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Total de Cartelas</div>
                        <div class='metric-value'>{total_itensct:.0f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<h1>🏢 Setores</h1>", unsafe_allow_html=True)

        sub_col1, sub_col2, sub_col3, sub_col4= st.columns([1,3,3,1])

        total_separacao = len(df_filtrado[df_filtrado['Setor'] == 'Separação'])
        total_compras = len(df_filtrado[df_filtrado['Setor'] == 'Compras'])
        total_embalagem = len(df_filtrado[df_filtrado['Setor'] == 'Embalagem'])
        total_expedicao = len(df_filtrado[df_filtrado['Setor'] == 'Expedição'])

        with sub_col2:
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Separação</div>
                        <div class='metric-value'>{valor_total_separacao_formatado}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with sub_col3:
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Compras</div>
                        <div class='metric-value'>{valor_total_compras_formatado}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        sub_col1, sub_col2, sub_col3, sub_col4= st.columns([1,3,3,1])

        with sub_col2:
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Embalagem</div>
                        <div class='metric-value'>{valor_total_embalagem_formatado}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with sub_col3:
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Expedição</div>
                        <div class='metric-value'>{valor_total_expedicao_formatado}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
    with col_direita:
        sub_col1, sub_col2= st.columns(2)
    
        with sub_col1:            
            valor_total_entregues = df[
                (pd.to_datetime(df['Dt.fat.'], errors='coerce').dt.month == current_date.month) &
                (pd.to_datetime(df['Dt.fat.'], errors='coerce').dt.year == current_date.year)
            ]['Valor Total'].sum()
            valor_total_entregues_formatado = f"R${valor_total_entregues:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f"""
                <div class='styled-col'>
                <div class='metric-container'>
                    <div class='metric-label'>Faturamento Total</div>
                    <div class='metric-value'>{valor_total_entregues_formatado}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with sub_col2:
            valor_total_pendencias = carteira[carteira['Status'] == 'Pendente']['Valor Total'].sum()
            valor_total_atrasados = carteira[carteira['Status'] == 'Atrasado']['Valor Total'].sum()
            valor_total_saldo = valor_total_pendencias + valor_total_atrasados
            valor_total_saldo_formatado = f"R${valor_total_saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f"""
                <div class='styled-col'>
                    <div class='metric-container'>
                        <div class='metric-label'>Valor Total de Saldo</div>
                        <div class='metric-value'>{valor_total_saldo_formatado}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
       
        carteira_entregue = carteira[carteira['Status'] == 'Entregue']

        carteira_entregue['Dt.fat.'] = pd.to_datetime(carteira_entregue['Dt.fat.'], errors='coerce')
        carteira_entregue['Mes'] = carteira_entregue['Dt.fat.'].dt.month
        carteira_entregue['Ano'] = carteira_entregue['Dt.fat.'].dt.year

        meses = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
        5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }
        carteira_entregue['Mes_Nome'] = carteira_entregue['Mes'].map(meses)

        df_agrupado = carteira_entregue.groupby(['Mes_Nome', 'Ano'])['Valor Total'].sum().reset_index()

        ordem_meses = list(meses.values())
        df_agrupado['Mes_Nome'] = pd.Categorical(df_agrupado['Mes_Nome'], categories=ordem_meses, ordered=True)
        df_agrupado = df_agrupado.sort_values(by='Mes_Nome')

        dados_2024 = df_agrupado[df_agrupado['Ano'] == 2024]
        dados_2025 = df_agrupado[df_agrupado['Ano'] == 2025]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=dados_2024["Mes_Nome"],
            y=dados_2024["Valor Total"],
            name="2024",
            marker_color="royalblue"
        ))

        fig.add_trace(go.Bar(
            x=dados_2025["Mes_Nome"],
            y=dados_2025["Valor Total"],
            name="2025",
            marker_color="red"
        ))

        fig.update_layout(
            title="Comparativo de Faturamento Mensal",
            xaxis_title="Meses",
            yaxis_title="Faturamento (R$)",
            barmode="group",
            legend_title="Ano",
            height=375
        )

        st.plotly_chart(fig)

        sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)

        with sub_col1:
            fig_indicador1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_separacao,
            title={'text': "Separação", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [None, 1000], 'visible': False},
                'bar': {'color': "rgb(9, 71, 128)"},
                'bgcolor': "white",
                'borderwidth': 1.5,
                'bordercolor': "skyblue",
                'steps': [
                    {'range': [0, 1000], 'color': 'lightgray'}
                ],
                }
            ))
            fig_indicador1.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=130
            )
            st.plotly_chart(fig_indicador1, use_container_width=True)

        with sub_col2:
            fig_indicador2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_compras,
            title={'text': "Compras", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [None, 1000], 'visible': False},
                'bar': {'color': "rgb(9, 71, 128)"},
                'bgcolor': "white",
                'borderwidth': 1.5,
                'bordercolor': "skyblue",
                'steps': [
                    {'range': [0, 1000], 'color': 'lightgray'}
                ],
            }
        ))
            fig_indicador2.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=130
            )
            st.plotly_chart(fig_indicador2, use_container_width=True)

        with sub_col3:
            fig_indicador3 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_embalagem,
                title={'text': "Embalagem", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [None, 1000], 'visible': False},
                    'bar': {'color': "rgb(9, 71, 128)"},
                    'bgcolor': "white",
                    'borderwidth': 1.5,
                    'bordercolor': "skyblue",
                    'steps': [
                        {'range': [0, 1000], 'color': 'lightgray'}
                    ],
                }
            ))
            fig_indicador3.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=130 
            )
            st.plotly_chart(fig_indicador3, use_container_width=True)


        with sub_col4:
            fig_indicador4 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_expedicao,
                title={'text': "Expedição", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [None, 1000], 'visible': False},
                    'bar': {'color': "rgb(9, 71, 128)"},
                    'bgcolor': "white",
                    'borderwidth': 1.5,
                    'bordercolor': "skyblue",
                    'steps': [
                        {'range': [0, 1000], 'color': 'lightgray'}
                    ],
                }
            ))
            fig_indicador4.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=130 
            )
            st.plotly_chart(fig_indicador4, use_container_width=True)

            pendencias_df = carteira[(carteira['Status'] == 'Pendente') | (carteira['Status'] == 'Atrasado')].copy()

    colunas_remover = [
        'Valor Unit.', 'Qtd.a produzir', 'Qtd. Produzida', 'Qtd.a liberar',
        'Prev.entrega', 'Dt.fat.',
    ]
    pendencias_df = pendencias_df.drop(columns=[col for col in colunas_remover if col in pendencias_df.columns])

    if 'Dt.pedido' in pendencias_df.columns:
        pendencias_df['Dt.pedido'] = pd.to_datetime(
            pendencias_df['Dt.pedido'], errors='coerce'
        )

    valor_inicial_dict = carteira.groupby('Ped. Cliente')['Valor Total'].sum().to_dict()
    valor_saldo_dict = pendencias_df.groupby('Ped. Cliente')['Valor Total'].sum().to_dict()
    pendencias_df['VALOR INICIAL'] = pendencias_df['Ped. Cliente'].map(valor_inicial_dict)
    pendencias_df['VALOR SALDO'] = pendencias_df['Ped. Cliente'].map(valor_saldo_dict)

    if not pendencias_df.empty:
        def gerar_excel_pendencias(df):
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='LISTA CORRIDA')
                workbook  = writer.book
                worksheet = writer.sheets['LISTA CORRIDA']
                if 'Dt.pedido' in df.columns:
                    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
                    col_idx = df.columns.get_loc('Dt.pedido')
                    worksheet.set_column(col_idx, col_idx, 12, date_format)

                setores = ['Separação', 'Compras', 'Embalagem', 'Expedição', 'Sem OE']

                mapa_pivot = df.pivot_table(
                    index=['Fantasia', 'Ped. Cliente', 'Dt.pedido', 'VALOR INICIAL', 'VALOR SALDO'],
                    columns='Setor',
                    values='Valor Total',
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()

                for setor in setores:
                    if setor not in mapa_pivot.columns:
                        mapa_pivot[setor] = 0

                for setor in setores:
                    valor_col = setor
                    perc_col = f'% {setor.upper()}'
                    mapa_pivot[perc_col] = (mapa_pivot[valor_col] / mapa_pivot['VALOR INICIAL']).replace([float('inf'), -float('inf')], 0).fillna(0).map(lambda x: f"{x:.0%}")

                mapa_pivot = mapa_pivot.rename(columns={
                    'Fantasia': 'CLIENTE',
                    'Ped. Cliente': 'PED.',
                    'Dt.pedido': 'DT',
                    'Separação': 'R$ SEPARAÇÃO',
                    'Compras': 'R$ COMPRAS',
                    'Embalagem': 'R$ EMBALAGEM',
                    'Expedição': 'R$ EXPEDIÇÃO',
                    'Sem OE': 'R$ SEM OE',
                    '% SEPARAÇÃO': '% SEPARAÇÃO',
                    '% COMPRAS': '% COMPRAS',
                    '% EMBALAGEM': '% EMBALAGEM',
                    '% EXPEDIÇÃO': '% EXPEDIÇÃO',
                    '% SEM OE': '% SEM OE'
                })

                mapa_pivot[''] = ''
                mapa_pivot['  '] = ''  

                colunas_final = [
                    'CLIENTE', 'PED.', 'DT', 'VALOR INICIAL', 'VALOR SALDO', '',
                    'R$ SEPARAÇÃO', '%',
                    'R$ COMPRAS', '%',
                    'R$ EMBALAGEM', '%',
                    'R$ EXPEDIÇÃO', '%', '  ',
                    'R$ SEM OE', '% SEM OE'
                ]
                for col in colunas_final:
                    if col not in mapa_pivot.columns:
                        mapa_pivot[col] = 0 if 'R$' in col or 'VALOR' in col else ''

                mapa_pivot = mapa_pivot[colunas_final]

                # Escreve a segunda aba
                mapa_pivot.to_excel(writer, index=False, sheet_name='CARTEIRA')

                # Formatar coluna DT como data dd/mm/yyyy na segunda aba
                worksheet2 = writer.sheets['CARTEIRA']
                if 'DT' in mapa_pivot.columns:
                    col_idx2 = mapa_pivot.columns.get_loc('DT')
                    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
                    worksheet2.set_column(col_idx2, col_idx2, 12, date_format)

            buffer.seek(0)
            return buffer

        excel_pendencias = gerar_excel_pendencias(pendencias_df)

        hoje = datetime.now()
        nome_arquivo = f"CARTEIRA FOXMIX {hoje.day:02d}.{hoje.month:02d}.xlsx"

        st.download_button(
            label="Exportar Relatório de Pendências",
            data=excel_pendencias,
            file_name=nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Nenhuma pendência encontrada para exportação.")
        
perfil_opcao = ("Administrador ⚙️")

if perfil_opcao == "Administrador ⚙️":
    admin_opcao = st.sidebar.radio("Opções do Administrador", ("Dashboard", "Notificações"))
    
    if admin_opcao == "Dashboard":
        guia_dashboard()