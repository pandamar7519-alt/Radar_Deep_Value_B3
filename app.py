import streamlit as st
import pandas as pd
import fundamentus
import math

# Configuração da Página
st.set_page_config(page_title="Radar B3 - Graham & Deep Value", layout="wide")

@st.cache_data(ttl=3600)
def load_and_process_data():
    # 1. Coleta os dados brutos
    df = fundamentus.get_resultado()
    
    # 2. Transforma o índice (Ticker) em coluna e reseta tudo
    df = df.reset_index()
    
    # 3. Força todos os nomes de colunas para minúsculas para evitar conflitos
    df.columns = [str(col).lower() for col in df.columns]
    
    # 4. Mapeamento de colunas com verificação de existência
    # Se a coluna não existir, o sistema cria com valor zero para não quebrar
    colunas_necessarias = ['papel', 'cotacao', 'pvp', 'dy', 'lpa', 'vpa']
    for col in colunas_necessarias:
        if col not in df.columns:
            df[col] = 0.0
            
    # 5. Seleciona e renomeia para o padrão do projeto
    df = df[colunas_necessarias].copy()
    df.columns = ['Ticker', 'Preço', 'P/VP', 'DY', 'LPA', 'VPA']
    
    # 6. Cálculo do Preço Justo de Graham
    def calcular_graham(row):
        try:
            # Requisito Graham: Lucro e Patrimônio positivos
            if row['LPA'] > 0 and row['VPA'] > 0:
                return math.sqrt(22.5 * row['LPA'] * row['VPA'])
        except:
            return 0
        return 0

    df['Preço Justo (Graham)'] = df.apply(calcular_graham, axis=1)
    
    # 7. Cálculo da Margem de Segurança
    df['Margem de Segurança'] = df.apply(
        lambda x: ((x['Preço Justo (Graham)'] - x['Preço']) / x['Preço Justo (Graham)'] * 100) 
        if x['Preço Justo (Graham)'] > x['Preço'] else 0, axis=1
    )
    
    # Ajuste do Dividend Yield para porcentagem
    df['DY'] = df['DY'] * 100
    
    return df

# --- UI INTERFACE ---
st.title("🏛️ Radar B3: Inteligência de Valor")
st.markdown("Critérios: Preço < R$ 20 | P/VP < 1 | Margem de Segurança > 0")

try:
    with st.spinner('Sincronizando com a B3...'):
        data = load_and_process_data()

    # Aplicação dos Filtros de Deep Value
    mask = (data['Preço'] < 20.00) & (data['P/VP'] < 1.0) & (data['P/VP'] > 0) & (data['Margem de Segurança'] > 0)
    df_filtrado = data[mask].sort_values(by='Margem de Segurança', ascending=False)

    if not df_filtrado.empty:
        st.subheader(f"✅ {len(df_filtrado)} Oportunidades Encontradas")
        st.dataframe(
            df_filtrado,
            column_config={
                "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
                "P/VP": st.column_config.NumberColumn(format="%.2f"),
                "DY": st.column_config.NumberColumn(format="%.2f%%"),
                "Preço Justo (Graham)": st.column_config.NumberColumn(format="R$ %.2f"),
                "Margem de Segurança": st.column_config.NumberColumn(format="%.2f%%")
            },
            hide_index=True, width='stretch'
        )
    else:
        st.warning("Nenhuma ação atende a todos os critérios simultâneos neste momento.")

except Exception as e:
    st.error(f"Erro de Processamento: {e}")

st.sidebar.caption("Versão do Motor: 2.0 (Resiliente)")
