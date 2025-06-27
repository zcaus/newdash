import pandas as pd
import re

# -------- CONFIGURAÇÕES --------
ARQUIVO_ENTRADA = "planilha/prontaparamescla.xlsx"
ARQUIVO_SAIDA   = "planilha/controledosistema.xlsx"
COL_PEDIDO      = "Nr.pedido"  # Altere se necessário
# -------------------------------

# 1) Carrega a planilha
df = pd.read_excel(ARQUIVO_ENTRADA)

# 2) Converte colunas numéricas
df['Qtd.a produzir'] = pd.to_numeric(df['Qtd.a produzir'], errors='coerce')
df['Qtd.a liberar'] = pd.to_numeric(df['Qtd.a liberar'], errors='coerce')
df['Qtd. Produzida'] = pd.to_numeric(df['Qtd. Produzida'], errors='coerce')

# 2.5) Trata casos de abastecimento parcial (liberação e produção parciais)
linhas_expandidas = []

for _, row in df.iterrows():
    qtd_produzir  = float(row.get("Qtd.a produzir", 0) or 0)
    qtd_liberar   = float(row.get("Qtd.a liberar", 0) or 0)
    qtd_produzida = float(row.get("Qtd. Produzida", 0) or 0)

    # Cálculo de quantidade possível para Expedição (ambas preenchidas)
    qtd_validada = min(qtd_liberar, qtd_produzida)

    if qtd_validada > 0:
        # Linha válida (Expedição, Embalagem ou similar)
        linha1 = row.copy()
        linha1["Qtd.a produzir"] = qtd_validada
        linha1["Qtd.a liberar"] = qtd_validada if qtd_liberar >= qtd_validada else None
        linha1["Qtd. Produzida"] = qtd_validada if qtd_produzida >= qtd_validada else None
        linhas_expandidas.append(linha1)

        sobra = qtd_produzir - qtd_validada
        if sobra > 0:
            # Linha para o saldo pendente (Compras)
            linha2 = row.copy()
            linha2["Qtd.a produzir"] = sobra
            linha2["Qtd.a liberar"] = None
            linha2["Qtd. Produzida"] = None
            linha2["ForçadoCompras"] = True
            linhas_expandidas.append(linha2)
    else:
        # Nenhuma combinação válida, manter linha original
        linhas_expandidas.append(row)

df = pd.DataFrame(linhas_expandidas)

# 3) Define o setor e motivo
def definir_setor_status(row):
    if row.get("ForçadoCompras") == True:
        return "Compras", "Quantidade pendente"

    dt_fat = row.get('Dt.fat.')
    qtd_produzida = row.get('Qtd. Produzida', 0)
    qtd_liberada  = row.get('Qtd.a liberar', 0)

    if pd.notnull(dt_fat) and dt_fat != "  /  /":
        return "Entregue", "Pedido já faturado"

    if pd.isnull(qtd_produzida) and pd.isnull(qtd_liberada):
        return "Separação", "Primeira separação"

    if (pd.isnull(qtd_produzida) or qtd_produzida == 0) and (qtd_liberada > 0):
        return "Embalagem", "Abastecido para embalagem"

    if qtd_produzida > 0 and qtd_liberada > 0:
        return "Expedição", "Produzido e liberado para expedição"

    return "Compras", "Sem Matéria-prima"

# Aplica a função
df[['Setor', 'Status lógico']] = df.apply(definir_setor_status, axis=1, result_type="expand")

# 4) Lógica de desmembramento
def extrair_base_sufixo(cod):
    if pd.isna(cod):
        return (None, None)
    cod = str(cod).strip()
    m = re.search(r"^(.*?)-(\d+)$", cod)
    if m:
        base = m.group(1)
        sufixo = int(m.group(2))
    else:
        base = cod
        sufixo = 1
    return (base, sufixo)

bases, sufixos = zip(*df[COL_PEDIDO].apply(extrair_base_sufixo))
df["PedidoBase"] = bases
df["Sufixo"] = sufixos

tem_desmembrado = df.groupby("PedidoBase")["Sufixo"].transform(lambda s: (s >= 2).any())

# Força Expedição por desmembramento (mas só se não estiver já como Entregue)
mask = (tem_desmembrado & (df["Sufixo"] == 1) & (df["Setor"] != "Entregue"))
df.loc[mask, "Setor"] = "Expedição"
df.loc[mask, "Status lógico"] = "Encontrado na primeira separação"

# 5) Cria coluna "Se iguais"
def comparar_linhas(row):
    if row.get("Qtd.a produzir") == row.get("Qtd. Produzida"):
        return "Iguais"
    else:
        return "Diferentes"

df['Se iguais'] = df.apply(comparar_linhas, axis=1)

# 6) Reorganiza colunas: insere "Se iguais" depois de "Setor", e "Status lógico" depois de "Se iguais"
colunas = list(df.columns)
for col in ["Se iguais", "Status lógico"]:
    if col in colunas:
        colunas.remove(col)

if "Setor" in colunas:
    setor_index = colunas.index("Setor")
    colunas.insert(setor_index + 1, "Se iguais")
    colunas.insert(setor_index + 2, "Status lógico")

df = df[colunas]

# 7) Salva a planilha final
df.to_excel(ARQUIVO_SAIDA, index=False)
print(f"✅ Planilha salva em: {ARQUIVO_SAIDA}")
