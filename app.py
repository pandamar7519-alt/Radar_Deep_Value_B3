import streamlit as st
import pandas as pd
import fundamentus

# Configuração da Página
st.set_page_config(page_title="Radar B3 - Deep Value", layout="wide")

@st.cache_data(ttl=3600) # Cache de 1 hora para performance
def load_data():
    # Obtendo dados fundamentais da B3
    df = fundamentus.get_resultado()
    
    # Limpeza e Renomeação para clareza
    df = df.reset_index()
    df = df[['papel', 'setor', 'cotacao', 'pvp', 'dy']]
    df.columns = ['Ticker', 'Setor', 'Preço Atual', 'P/VP', 'Dividend Yield']
    
    # Transformando decimais (Fundamentus traz em escala de 100 as vezes)
    df['Dividend Yield'] = df['Dividend Yield'] * 100
    
    return df

# --- UI INTERFACE ---
st.title("🏛️ Arquiteto de Soluções: Radar Deep Value B3")
st.markdown("Busca automatizada por ativos subvalorizados ($P/VP < 1$) com preço acessível.")

try:
    with st.spinner('Escaneando o mercado...'):
        data = load_data()

    # --- APLICAÇÃO DOS FILTROS DO PROMPT ---
    # 1. Preço < R$ 20.00
    # 2. P/VP < 1.0 (E maior que 0 para evitar empresas com PL negativo)
    filtro = (data['Preço Atual'] < 20.00) & (data['P/VP'] < 1.0) & (data['P/VP'] > 0)
    df_filtrado = data[filtro].sort_values(by='P/VP')

    # --- EXIBIÇÃO POR SETOR ---
    setores = df_filtrado['Setor'].unique()

    for setor in setores:
        with st.expander(f"📁 Setor: {setor}", expanded=True):
            df_setor = df_filtrado[df_filtrado['Setor'] == setor]
            st.dataframe(
                df_setor, 
                column_config={
                    "Preço Atual": st.column_config.NumberColumn(format="R$ %.2f"),
                    "P/VP": st.column_config.NumberColumn(format="%.2f"),
                    "Dividend Yield": st.column_config.NumberColumn(format="%.2f%%")
                },
                hide_index=True,
                use_container_width=True
            )

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")

st.sidebar.info("Critérios: Preço < R$ 20.00 | P/VP < 1.0 | Foco: Longo Prazo")
