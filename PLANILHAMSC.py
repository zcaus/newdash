import pandas as pd

planilha1 = pd.read_excel("planilha/PEDIDOS.XLSX", sheet_name="Planilha1")
planilha2 = pd.read_excel("planilha/ABASTECIDOS.XLSX", sheet_name="Planilha2")

planilha1['Ped. Cliente'] = planilha1['Ped. Cliente'].astype(str)
planilha2['Ped. Cliente'] = planilha2['Ped. Cliente'].astype(str)

planilha1_com_hifen = planilha1[planilha1['Nr.pedido'].str.contains('-')]
planilha1_sem_hifen = planilha1[~planilha1['Nr.pedido'].str.contains('-')]

colunas_comuns = ["Ped. Cliente", "Modelo", "Produto"]
planilha_mesclada_com_hifen = pd.merge(planilha1_com_hifen, planilha2, on=colunas_comuns, how="outer", suffixes=('_planilha1', '_planilha2'))

planilha_mesclada = pd.concat([planilha_mesclada_com_hifen, planilha1_sem_hifen]).reset_index(drop=True)

with pd.ExcelWriter("planilha/controledosistema.xlsx", engine='openpyxl', mode='w') as writer:
    planilha_mesclada.to_excel(writer, index=False, sheet_name='Planilha1')

print("Planilha mesclada criada com sucesso.")