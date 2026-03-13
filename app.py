import streamlit as st
import pandas as pd
import fundamentus
import math

# Configuração da Página
st.set_page_config(page_title="Radar B3 - Inteligência Graham", layout="wide")

@st.cache_data(ttl=3600)
def load_and_process_data():
    # Coleta bruta de dados
    df_raw = fundamentus.get_resultado()
    df = df_raw.reset_index()
    
    # Padronização: Convertendo todos os nomes de colunas para minúsculas
    # Isso evita o erro de "not in index" se a API mudar entre maiúsculas/minúsculas
    df.columns = [str(col).lower() for col in df.columns]
    
    # Seleção segura das colunas necessárias
    colunas_foco = {
        'papel': 'Ticker',
        'cotacao': 'Preço',
        'pvp': 'P/VP',
        'dy': 'DY',
        'lpa': 'LPA',
        'vpa': 'VPA'
    }
    
    # Filtramos apenas o que existe no DataFrame
    df = df[list(colunas_foco.keys())]
    df.rename(columns=colunas_foco, inplace=True)
    
    # Cálculo do Preço Justo de Graham: sqrt(22.5 * LPA * VPA)
    def calcular_graham(row):
        try:
            # Graham só se aplica a empresas com lucro e patrimônio positivos
            if row['LPA'] > 0 and row['VPA'] > 0:
                val = 22.5 * row['LPA'] * row['VPA']
                return math.sqrt(val)
        except:
            return 0
        return 0

    df['Preço Justo (Graham)'] = df.apply(calcular_graham, axis=1)
    
    # Cálculo da Margem de Segurança (%)
    df['Margem de Segurança'] = df.apply(
        lambda x: ((x['Preço Justo (Graham)'] - x['Preço']) / x['Preço Justo (Graham)'] * 100) 
        if x['Preço Justo (Graham)'] > 0 else -100, axis=1
    )
    
    # Ajuste do DY (API traz em decimal, ex: 0.10 para 10%)
    df['DY'] = df['DY'] * 100
    
    return df

# --- UI INTERFACE ---
st.title("🏛️ Radar B3: Deep Value & Margem de Segurança")
st.markdown("Estratégia: Preço < R$ 20 | P/VP < 1 | Margem de Segurança Graham > 0.")

try:
    with st.spinner('Acessando dados e calculando Preço Justo...'):
        data = load_and_process_data()

    # Filtros Rigorosos de Projeto
    filtro = (data['Preço'] < 20.00) & (data['P/VP'] < 1.0) & (data['P/VP'] > 0) & (data['Margem de Segurança'] > 0)
    df_final = data[filtro].sort_values(by='Margem de Segurança', ascending=False)

    st.subheader(f"📊 {len(df_final)} Ativos com Desconto Patrimonial")
    
    # Exibição com largura otimizada
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
    st.error(f"Erro técnico detectado: {e}")
    st.info("Dica: Verifique se a biblioteca 'fundamentus' está na versão 0.3.2 no seu requirements.txt.")

st.sidebar.write("---")
st.sidebar.caption("Fórmula de Graham: V.I. = √(22,5 * LPA * VPA)")
