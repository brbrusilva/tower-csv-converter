import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Conversor Tower", layout="centered")

st.title("📦 Conversor de Tabelas para o Tower")

uploaded_file = st.file_uploader("Faça upload do arquivo CSV (até 10MB)", type="csv")

def detectar_tipo(colunas):
    if 'WEIGHTSTART' in colunas and 'PRICE' in colunas:
        return "frete_peso"
    elif 'zip_code_start' in colunas and 'advalorem' in colunas:
        return "abrangencia"
    else:
        return "desconhecido"

def padronizar_frete_peso(df):
    colunas_padrao = ['CARRIER', 'ORIGIN_UF', 'REGION', 'WEIGHTSTART', 'WEIGHTEND',
                      'PRICE', 'ORIGIN_CITY', 'TIER', 'VIGENCIASTART', 'VIGENCIAEND']
    return df[colunas_padrao]

def padronizar_abrangencia(df):
    colunas_padrao = ['origin_uf', 'origin_city', 'state', 'city', 'zip_code_start',
                      'zip_code_end', 'slo', 'region', 'gris', 'advalorem',
                      'shipping_label', 'date_start', 'date_end']
    return df[colunas_padrao]

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        tipo = detectar_tipo(df.columns)

        if tipo == "frete_peso":
            df_padrao = padronizar_frete_peso(df)
            nome_saida = "frete_peso_tower.csv"
        elif tipo == "abrangencia":
            df_padrao = padronizar_abrangencia(df)
            nome_saida = "abrangencia_tower.csv"
        else:
            st.error("❌ Não foi possível detectar o tipo de tabela. Verifique o formato.")
            st.stop()

        st.success(f"✅ Tabela do tipo **{tipo}** reconhecida e padronizada com sucesso!")

        st.download_button(
            label="📥 Baixar CSV Convertido",
            data=df_padrao.to_csv(index=False).encode("utf-8"),
            file_name=nome_saida,
            mime="text/csv"
        )

        st.dataframe(df_padrao)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
