import streamlit as st
import pandas as pd
import fundamentus
import math

# Configuração da Página
st.set_page_config(page_title="Radar B3 - Valor & Graham", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    # Coleta bruta
    df = fundamentus.get_resultado()
    df = df.reset_index()
    
    # Padronização de colunas (Minúsculas para evitar erros de índice)
    df.columns = [str(col).lower() for col in df.columns]
    
    # Mapeamento essencial
    cols = {'papel': 'Ticker', 'cotacao': 'Preço', 'pvp': 'P/VP', 'dy': 'DY', 'lpa': 'LPA', 'vpa': 'VPA'}
    df = df[list(cols.keys())].copy()
    df.rename(columns=cols, inplace=True)
    
    # Cálculo do Preço Justo de Graham (Apenas para empresas lucrativas)
    def calculate_graham(row):
        try:
            if row['LPA'] > 0 and row['VPA'] > 0:
                return math.sqrt(22.5 * row['LPA'] * row['VPA'])
        except: return 0
        return 0

    df['Preço Justo (Graham)'] = df.apply(calculate_graham, axis=1)
    
    # Margem de Segurança (Se não houver Graham, fica como 'N/A')
    df['Margem'] = df.apply(
        lambda x: round(((x['Preço Justo (Graham)'] - x['Preço']) / x['Preço Justo (Graham)'] * 100), 2)
        if x['Preço Justo (Graham)'] > 0 else None, axis=1
    )
    
    df['DY'] = df['DY'] * 100
    return df

# --- INTERFACE ---
st.title("🏛️ Radar B3: Oportunidades de Valor")
st.markdown("Filtros Base: Preço < R$ 20 e P/VP < 1.0")

try:
    with st.spinner('Escaneando mercado...'):
        data = load_data()

    # Filtro Original (Preço e P/VP) para garantir que as ações apareçam
    mask = (data['Preço'] < 20.00) & (data['P/VP'] < 1.0) & (data['P/VP'] > 0)
    df_result = data[mask].sort_values(by='P/VP')

    # Métricas de Resumo
    col1, col2 = st.columns(2)
    col1.metric("Ações Encontradas", len(df_result))
    col2.metric("Com Margem Graham", len(df_result[df_result['Margem'] > 0]))

    st.dataframe(
        df_result,
        column_config={
            "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
            "P/VP": st.column_config.NumberColumn(format="%.2f"),
            "DY": st.column_config.NumberColumn(format="%.2f%%"),
            "Preço Justo (Graham)": st.column_config.NumberColumn(format="R$ %.2f"),
            "Margem": st.column_config.NumberColumn(format="%.2f%%", label="Margem Graham")
        },
        hide_index=True, width='stretch'
    )

except Exception as e:
    st.error(f"Erro: {e}")

st.sidebar.info("As ações sem 'Margem Graham' são empresas que atualmente operam com lucro negativo ou patrimônio ajustado.")
