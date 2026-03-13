import streamlit as st
import pandas as pd
import fundamentus
import math

# Configuração da Página
st.set_page_config(page_title="Radar Deep Value - Estratégia Graham", layout="wide")

@st.cache_data(ttl=3600)
def load_and_process_data():
    # Coleta de dados fundamentais
    df = fundamentus.get_resultado()
    df = df.reset_index()
    
    # Selecionando e renomeando colunas cruciais
    # lpa = Lucro por Ação | vpa = Valor Patrimonial por Ação
    df = df[['papel', 'cotacao', 'pvp', 'dy', 'lpa', 'vpa', 'p_l']]
    df.columns = ['Ticker', 'Preço', 'P/VP', 'DY', 'LPA', 'VPA', 'P_L']
    
    # 1. Filtro de Dividendos Ininterruptos (Simulação via DY positivo e histórico)
    # Nota: A API fundamentus traz o DY atual. Filtramos DY > 0 para garantir pagadoras.
    df = df[df['DY'] > 0]
    
    # 2. Cálculo do Preço Justo de Graham
    def calcular_graham(row):
        if row['LPA'] > 0 and row['VPA'] > 0:
            return math.sqrt(22.5 * row['LPA'] * row['VPA'])
        return 0

    df['Preço Justo (Graham)'] = df.apply(calcular_graham, axis=1)
    
    # 3. Cálculo da Margem de Segurança (%)
    df['Margem de Segurança'] = ((df['Preço Justo (Graham)'] - df['Preço']) / df['Preço Justo (Graham)']) * 100
    
    return df

# --- UI INTERFACE ---
st.title("🏛️ Radar B3: Inteligência Graham & Deep Value")
st.markdown("Filtros avançados: Preço < R$ 20 | P/VP < 1 | Margem de Segurança Positiva.")

try:
    data = load_and_process_data()

    # Aplicação dos Filtros do Projeto
    filtro = (data['Preço'] < 20.00) & (data['P/VP'] < 1.0) & (data['P/VP'] > 0) & (data['Margem de Segurança'] > 0)
    df_final = data[filtro].sort_values(by='Margem de Segurança', ascending=False)

    # Exibição das Top 10 Oportunidades
    st.subheader("🏆 Top 10 Ações com Maior Margem de Segurança")
    st.dataframe(
        df_final.head(10),
        column_config={
            "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
            "P/VP": st.column_config.NumberColumn(format="%.2f"),
            "DY": st.column_config.NumberColumn(format="%.2f%%"),
            "Preço Justo (Graham)": st.column_config.NumberColumn(format="R$ %.2f"),
            "Margem de Segurança": st.column_config.NumberColumn(format="%.2f%%")
        },
        hide_index=True, use_container_width=True
    )

    # Botão para Download (Simulando o relatório em PDF/CSV)
    st.sidebar.header("Relatórios")
    csv = df_final.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📩 Baixar Relatório Completo (CSV)", csv, "radar_b3.csv", "text/csv")

except Exception as e:
    st.error(f"Erro na análise quantitativa: {e}")

st.sidebar.info("A fórmula de Graham ajuda a identificar quanto o ativo deveria valer com base no lucro e patrimônio.")
