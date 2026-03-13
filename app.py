import streamlit as st
import pandas as pd
import fundamentus
import math

# Configuração da Página
st.set_page_config(page_title="Radar B3 - Deep Value", layout="wide")

@st.cache_data(ttl=3600)
def load_and_process_data():
    # Coleta de dados
    df = fundamentus.get_resultado()
    df = df.reset_index()
    
    # Mapeamento dinâmico para evitar o erro "not in index"
    # A biblioteca costuma usar maiúsculas para os indicadores
    df = df[['papel', 'cotacao', 'pvp', 'dy', 'lpa', 'vpa']]
    df.columns = ['Ticker', 'Preço', 'P/VP', 'DY', 'LPA', 'VPA']
    
    # Cálculo do Preço Justo de Graham: sqrt(22.5 * LPA * VPA)
    def calcular_graham(row):
        try:
            if row['LPA'] > 0 and row['VPA'] > 0:
                return math.sqrt(22.5 * row['LPA'] * row['VPA'])
        except:
            return 0
        return 0

    df['Preço Justo (Graham)'] = df.apply(calcular_graham, axis=1)
    
    # Cálculo da Margem de Segurança
    # Evita divisão por zero
    df['Margem de Segurança'] = df.apply(
        lambda x: ((x['Preço Justo (Graham)'] - x['Preço']) / x['Preço Justo (Graham)'] * 100) 
        if x['Preço Justo (Graham)'] > 0 else -100, axis=1
    )
    
    return df

# --- UI INTERFACE ---
st.title("🏛️ Radar B3: Inteligência Graham & Deep Value")
st.markdown("Filtros: Preço < R$ 20 | P/VP < 1 | Margem de Segurança Positiva.")

try:
    with st.spinner('Calculando métricas quantitativas...'):
        data = load_and_process_data()

    # Aplicação dos Filtros solicitados
    filtro = (data['Preço'] < 20.00) & (data['P/VP'] < 1.0) & (data['P/VP'] > 0) & (data['Margem de Segurança'] > 0)
    df_final = data[filtro].sort_values(by='Margem de Segurança', ascending=False)

    st.subheader(f"🔍 {len(df_final)} Oportunidades Identificadas")
    
    # Exibição da Tabela
    # Note: Usei width='stretch' conforme sugerido pelos logs do Streamlit [cite: 14]
    st.dataframe(
        df_final,
        column_config={
            "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
            "P/VP": st.column_config.NumberColumn(format="%.2f"),
            "DY": st.column_config.NumberColumn(format="%.2f%%"),
            "Preço Justo (Graham)": st.column_config.NumberColumn(format="R$ %.2f"),
            "Margem de Segurança": st.column_config.NumberColumn(format="%.2f%%")
        },
        hide_index=True, 
        width='stretch'
    )

except Exception as e:
    st.error(f"Erro na análise: {e}")

st.sidebar.info("Este radar utiliza a Fórmula de Graham para encontrar o valor intrínseco.")
