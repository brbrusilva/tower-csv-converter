import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conversor Tower", layout="centered")
st.title("📦 Conversor de Tabelas para o Tower")

uploaded_file = st.file_uploader("Faça upload do arquivo CSV (até 10MB)", type="csv")

# Colunas padrão esperadas para cada tipo
colunas_frete_peso = {
    'CARRIER', 'ORIGIN_UF', 'REGION', 'WEIGHTSTART', 'WEIGHTEND',
    'PRICE', 'ORIGIN_CITY', 'TIER', 'VIGENCIASTART', 'VIGENCIAEND'
}
colunas_abrangencia = {
    'origin_uf', 'origin_city', 'state', 'city', 'zip_code_start',
    'zip_code_end', 'slo', 'region', 'gris', 'advalorem',
    'shipping_label', 'date_start', 'date_end'
}

def detectar_tipo(colunas):
    colunas_set = set(colunas)
    if len(colunas_frete_peso.intersection(colunas_set)) >= 6:
        return "frete_peso"
    elif len(colunas_abrangencia.intersection(colunas_set)) >= 6:
        return "abrangencia"
    else:
        return "desconhecido"

def padronizar_dataframe(df, tipo):
    if tipo == "frete_peso":
        colunas_presentes = [col for col in colunas_frete_peso if col in df.columns]
    elif tipo == "abrangencia":
        colunas_presentes = [col for col in colunas_abrangencia if col in df.columns]
    else:
        raise ValueError("Tipo de planilha desconhecido")

    df_padrao = df[colunas_presentes].copy()
    return df_padrao

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        tipo = detectar_tipo(df.columns)

        if tipo == "desconhecido":
            st.error("❌ Não foi possível identificar o tipo da planilha. Verifique se ela segue o padrão Tower.")
            st.stop()

        df_padronizado = padronizar_dataframe(df, tipo)
        st.success(f"✅ Planilha do tipo **{tipo}** reconhecida. Colunas convertidas com sucesso!")

        st.download_button(
            label="📥 Baixar CSV Convertido",
            data=df_padronizado.to_csv(index=False).encode("utf-8"),
            file_name=f"{tipo}_tower.csv",
            mime="text/csv"
        )

        st.dataframe(df_padronizado)

    except Exception as e:
        st.error("⚠️ Erro ao processar a planilha:")
        st.exception(e)
