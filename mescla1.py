import pandas as pd

# Leitura das planilhas
planilha1 = pd.read_excel("planilha/PEDIDOS.XLSX", sheet_name="Planilha1")
planilha2 = pd.read_excel("planilha/ABASTECIDOS.XLSX", sheet_name="Planilha2")

# Garantir que as colunas que serão usadas no merge tenham o mesmo tipo
planilha1['Ped. Cliente'] = planilha1['Ped. Cliente'].astype(str)
planilha2['Ped. Cliente'] = planilha2['Ped. Cliente'].astype(str)

# Definição das colunas em comum
colunas_comuns = ["Ped. Cliente", "Modelo", "Produto"]

# Realiza o merge utilizando as colunas em comum
planilha_mesclada = pd.merge(planilha1, planilha2, on=colunas_comuns, how="outer", 
                              suffixes=('_planilha1', '_planilha2'))

# Escrita da planilha mesclada em um novo arquivo Excel
with pd.ExcelWriter("planilha/prontaparamescla.xlsx", engine='openpyxl', mode='w') as writer:
    planilha_mesclada.to_excel(writer, index=False, sheet_name='Planilha1')

print("Planilha mesclada criada com sucesso.")
