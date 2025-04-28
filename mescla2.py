import pandas as pd

# Carrega a planilha completa
df = pd.read_excel("planilha/prontaparamescla.xlsx")  # ajuste o caminho conforme necessário

# Converte as colunas para numérico
df['AE'] = pd.to_numeric(df['Qtd. Produzida'], errors='coerce')
df['AF'] = pd.to_numeric(df['Qtd.a liberar'], errors='coerce')

def definir_setor(row):
    dt_fat = row.get('Dt.fat.')
    # Se a coluna 'Dt.fat.' estiver preenchida e não for "//", considera "Entregue"
    if pd.notnull(dt_fat) and dt_fat != "  /  /":
        return "Entregue"

    # Obtem os valores numéricos das colunas
    ae = row.get('Qtd. Produzida')
    af = row.get('Qtd.a liberar')
    
    # Se ambos os valores estiverem vazios (NaN), retorna "Separação"
    if pd.isnull(ae) and pd.isnull(af):
        return "Separação"
    
    # Se Qtd. Produzida for zero ou estiver ausente
    if pd.isnull(ae) or ae == 0:
        if pd.notnull(af) and af > 0:
            return "Embalagem"
        else:
            return "Compras"
    
    # Se Qtd. Produzida e Qtd.a liberar forem maiores que zero
    if ae > 0 and pd.notnull(af) and af > 0:
        return "Expedição"
    
    # Caso não se encaixe em nenhuma condição, retorna string vazia
    return ""

# Aplica a função para criar a coluna "Setor"
df['Setor'] = df.apply(definir_setor, axis=1)

# Cria a coluna "Se iguais" comparando "Qtd. Produzida" com "Qtd.a liberar"
def comparar_linhas(row):
    if row.get("Qtd.a produzir") == row.get("Qtd. Produzida"):
        return "Iguais"
    else:
        return "Diferentes"

df['Se iguais'] = df.apply(comparar_linhas, axis=1)

# Reordena as colunas para inserir "Se iguais" logo após "Setor", se necessário
colunas = list(df.columns)
if "Setor" in colunas and "Se iguais" in colunas:
    setor_index = colunas.index("Setor")
    colunas.remove("Se iguais")
    colunas.insert(setor_index + 1, "Se iguais")
    df = df[colunas]

# Salva a planilha atualizada
df.to_excel("planilha/controledosistema.xlsx", index=False)
