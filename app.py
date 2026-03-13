import streamlit as st
import pandas as pd
import fundamentus
import math

# Configuração da Página
st.set_page_config(page_title="Radar B3 - Valor & Graham", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    # Coleta bruta e reset de index imediato
    df = fundamentus.get_resultado()
    df = df.reset_index()
    
    # Padronização agressiva: minúsculas e remoção de espaços
    df.columns = [str(col).lower().strip() for col in df.columns]
    
    # Dicionário de busca flexível (Mapeamento de Sinônimos)
    # Se a API mudar 'lpa' para 'lucro_por_acao', o código ainda funciona
    mapa_flexivel = {
        'ticker': ['papel', 'ticker', 'index'],
        'preco': ['cotacao', 'preco', 'price'],
        'pvp': ['pvp', 'p/vp', 'p_vp'],
        'dy': ['dy', 'dividend_yield', 'dividendo'],
        'lpa': ['lpa', 'lucro_lpa', 'lucro_acao'],
        'vpa': ['vpa', 'valor_vpa', 'valor_patrimonial']
    }

    # Criando novo DataFrame com colunas garantidas
    df_clean = pd.DataFrame()
    
    for meta, sinonimos in mapa_flexivel.items():
        for col in df.columns:
            if col in sinonimos:
                df_clean[meta] = df[col]
                break
        if meta not in df_clean.columns:
            df_clean[meta] = 0.0 # Fallback de segurança

    # Renomeação final para exibição
    df_clean.columns = ['Ticker', 'Preço', 'P/VP', 'DY', 'LPA', 'VPA']
    
    # Cálculo do Preço Justo de Graham
    def calculate_graham(row):
        try:
            if row['LPA'] > 0 and row['VPA'] > 0:
                return math.sqrt(22.5 * row['LPA'] * row['VPA'])
        except: return 0
        return 0

    df_clean['Preço Justo (Graham)'] = df_clean.apply(calculate_graham, axis=1)
    
    # Margem de Segurança Graham (%)
    df_clean['Margem'] = df_clean.apply(
        lambda x: round(((x['Preço Justo (Graham)'] - x['Preço']) / x['Preço Justo (Graham)'] * 100), 2)
        if x['Preço Justo (Graham)'] > 0 else None, axis=1
    )
    
    # Normalização do DY
    df_clean['DY'] = df_clean['DY'] * 100
    
    return df_clean

# --- INTERFACE ---
st.title("🏛️ Radar B3: Inteligência de Valor")
st.markdown("Filtros Base: Preço < R$ 20 e P/VP < 1.0")

try:
    with st.spinner('Escaneando o mercado financeiro...'):
        data = load_data()

    # Filtro principal solicitado para garantir o volume de ações
    mask = (data['Preço'] < 20.00) & (data['P/VP'] < 1.0) & (data['P/VP'] > 0)
    df_result = data[mask].sort_values(by='P/VP')

    # Cartões de Inteligência
    c1, c2, c3 = st.columns(3)
    c1.metric("Ações Baratas (<R$20 & P/VP<1)", len(df_result))
    c2.metric("Com Margem de Segurança Graham", len(df_result[df_result['Margem'].fillna(-1) > 0]))
    c3.metric("Média P/VP do Grupo", round(df_result['P/VP'].mean(), 2))

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
    st.error(f"Ocorreu um erro inesperado: {e}")
    st.info("Verifique se a conexão com o servidor da B3 está ativa.")

st.sidebar.caption("Sistema de Busca Flexível Ativado (v3.0)")
