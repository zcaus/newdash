import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Função para carregar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel('planilha/controledosistema.xlsx')
    return df

# Função para definir status
def definir_status(df):
    df['Status'] = 'Pendente'
    df.loc[df['Setor'] == 'Entregue', 'Status'] = 'Entregue'
    return df

def main():
    # Carregar os dados
    df = carregar_dados()
    df = definir_status(df)

    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        clientes = df['Fantasia'].unique().tolist()
        clientes.append('Todos os clientes')
        cliente_selecionado = st.selectbox("Selecione um cliente", clientes)
    
    with col2:
        pedidos_cliente = df['Ped. Cliente'].unique().tolist()
        pedidos_cliente.append('Todos os pedidos')
        pedido_cliente_selecionado = st.selectbox("Selecione um pedido", pedidos_cliente)

    # Aplicar os filtros
    if cliente_selecionado == 'Todos os clientes':
        df_filtrado = df
    else:
        df_filtrado = df[df['Fantasia'] == cliente_selecionado]
    
    if pedido_cliente_selecionado != 'Todos os pedidos':
        df_filtrado = df_filtrado[df_filtrado['Ped. Cliente'] == pedido_cliente_selecionado]

    # Calcular métricas
    total_valPedido = df_filtrado['Valor Total'].sum()
    total_valEntregue = df_filtrado[df_filtrado['Status'] == 'Entregue']['Valor Total'].sum()
    total_valPendente = total_valPedido - total_valEntregue
    
    percentual_pendente = (total_valPendente / total_valPedido) * 100 if total_valPedido != 0 else 0
    total_linhas = len(df_filtrado)
    linhas_pendentes = total_linhas - len(df_filtrado[df_filtrado['Status'] == 'Entregue'])

    # Formatando os valores
    def formatar_moeda(valor):
        return f"R$ {valor:,.2f}"

    #Criar as métricas
    st.title("Monitoramento de Pedidos")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Pedidos (Linhas)", total_linhas)
    with col2:
        st.metric("Total Pendente (%)", f"{percentual_pendente:.2f}%")
    with col3:
        st.metric("Linhas Pendentes", linhas_pendentes)

    # Gráfico de Pizza do Saldo
    fig_pizza = px.pie(names=['Entregue', 'Pendente'],
                      values=[total_valEntregue, total_valPendente],
                      title="Distribuição do Valor do Pedido")
    st.plotly_chart(fig_pizza)

    # Gráfico de Barras Linhas Pendentes
    fig_bar = px.bar(df_filtrado[df_filtrado['Status'] == 'Pendente'], 
                   x='Setor', 
                   y='Qtd.',
                   title="Quantidade Pendente por Setor")
    st.plotly_chart(fig_bar)

    # Exibição dos Dados
    st.markdown("### Dados do Pedido Filtrados")
    st.dataframe(df_filtrado)

if __name__ == "__main__":
    main()