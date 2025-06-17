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
df['AE'] = pd.to_numeric(df['Qtd. Produzida'], errors='coerce')
df['AF'] = pd.to_numeric(df['Qtd.a liberar'], errors='coerce')

# 3) Define o setor e motivo
def definir_setor_status(row):
    dt_fat = row.get('Dt.fat.')
    ae = row.get('Qtd. Produzida')
    af = row.get('Qtd.a liberar')

    if pd.notnull(dt_fat) and dt_fat != "  /  /":
        return "Entregue", "Pedido já faturado"

    if pd.isnull(ae) and pd.isnull(af):
        return "Separação", "Sem produção e sem liberação"

    if pd.isnull(ae) or ae == 0:
        if pd.notnull(af) and af > 0:
            return "Embalagem", "Liberado para embalagem"
        else:
            return "Compras", "Sem produção e sem liberação"

    if ae > 0 and pd.notnull(af) and af > 0:
        return "Expedição", "Produzido e liberado para expedição"

    return "", ""

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
df.loc[mask, "Status lógico"] = "Expedição forçada por desmembramento"

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
