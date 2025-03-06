import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# 1. Carregar os dados do arquivo Excel
df = pd.read_excel('planilha/controledosistema.xlsx')

# 2. Conversão de colunas de data
df['Dt.pedido'] = pd.to_datetime(df['Dt.pedido'], errors='coerce')
df['Dt.fat.'] = pd.to_datetime(df['Dt.fat.'], errors='coerce')
df['Prev.entrega'] = pd.to_datetime(df['Prev.entrega'], errors='coerce')

# 3. Feature Engineering
# Tempo até faturamento (em dias)
df['tempo_faturamento'] = (df['Dt.fat.'] - df['Dt.pedido']).dt.days

# Tempo de entrega (em dias) - escolha Dt.fat. ou Dt.pedido como base
df['tempo_entrega'] = (df['Prev.entrega'] - df['Dt.fat.']).dt.days

# Validação dos valores: checar se Valor Total confere com Qtd. * Valor Unit.
df['valor_calculado'] = df['Qtd.'] * df['Valor Unit.']
df['valor_confere'] = np.isclose(df['Valor Total'], df['valor_calculado'])

# Exemplo: criar features temporais (mês do pedido)
df['mes_pedido'] = df['Dt.pedido'].dt.month

# 4. Seleção de Features e Target
# Neste exemplo, vamos prever o Valor Total com base no tempo de faturamento, Qtd. e Valor Unit.
X = df[['tempo_faturamento', 'Qtd.', 'Valor Unit.']]
y = df['Valor Total']

# 5. Divisão dos Dados (80% treino / 20% teste)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Treinamento do Modelo: Regressão Linear
modelo = LinearRegression()
modelo.fit(X_train, y_train)

# 7. Previsão e Avaliação
y_pred = modelo.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"RMSE: {rmse:.2f}")

# Visualização dos resultados
plt.scatter(y_test, y_pred, alpha=0.6)
plt.xlabel("Valor Total Real")
plt.ylabel("Valor Total Previsto")
plt.title("Previsão de Faturamento")
plt.show()
