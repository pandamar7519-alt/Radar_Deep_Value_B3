import streamlit as st
import pandas as pd
import fundamentus

# Configuração da Página
st.set_page_config(page_title="Radar B3 - Deep Value", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    # Obtendo dados fundamentais
    df = fundamentus.get_resultado()
    
    # Resetando o index para que o Ticker vire uma coluna
    df = df.reset_index()
    
    # A biblioteca mudou: vamos selecionar apenas as colunas financeiras existentes
    # 'cotacao' é o preço, 'pvp' é o P/VP, 'dy' é o Dividend Yield
    df = df[['papel', 'cotacao', 'pvp', 'dy']]
    df.columns = ['Ticker', 'Preço Atual', 'P/VP', 'Dividend Yield']
    
    # Ajustando escala do Dividend Yield
    df['Dividend Yield'] = df['Dividend Yield'] * 100
    
    return df

# --- UI INTERFACE ---
st.title("🏛️ Radar Deep Value B3")
st.markdown("Busca automatizada por ativos onde o preço é menor que o valor patrimonial.")

try:
    with st.spinner('Acessando dados da B3...'):
        data = load_data()

    # --- APLICAÇÃO DOS FILTROS ---
    # Filtro: Preço < 20 E P/VP entre 0 e 1.0
    filtro = (data['Preço Atual'] < 20.00) & (data['P/VP'] < 1.0) & (data['P/VP'] > 0)
    df_filtrado = data[filtro].sort_values(by='P/VP')

    # Exibição dos resultados em tabela única (já que a coluna Setor foi removida da fonte)
    st.subheader(f"🔍 Encontradas {len(df_filtrado)} oportunidades de Deep Value")
    
    st.dataframe(
        df_filtrado, 
        column_config={
            "Preço Atual": st.column_config.NumberColumn(format="R$ %.2f"),
            "P/VP": st.column_config.NumberColumn(format="%.2f"),
            "Dividend Yield": st.column_config.NumberColumn(format="%.2f%%")
        },
        hide_index=True,
        use_container_width=True
    )

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")

st.sidebar.info("Critérios: Preço < R$ 20.00 | P/VP < 1.0")
