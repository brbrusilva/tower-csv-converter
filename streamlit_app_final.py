import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conversor Tower", layout="centered")
st.title("📦 Conversor de Tabelas para o Tower")

uploaded_file = st.file_uploader("Faça upload da planilha (.csv, .xls ou .xlsx)", type=["csv", "xls", "xlsx"])

# Templates fixos
template_frete_peso = [
    'CARRIER', 'ORIGIN_UF', 'REGION', 'WEIGHTSTART', 'WEIGHTEND',
    'PRICE', 'ORIGIN_CITY', 'TIER', 'VIGENCIASTART', 'VIGENCIAEND'
]
template_abrangencia = [
    'origin_uf', 'origin_city', 'state', 'city', 'zip_code_start',
    'zip_code_end', 'slo', 'region', 'gris', 'advalorem',
    'shipping_label', 'date_start', 'date_end'
]

def detectar_tipo(colunas):
    colunas_set = set(colunas)
    match_frete = len(set(template_frete_peso).intersection(colunas_set))
    match_abrang = len(set(template_abrangencia).intersection(colunas_set))
    if match_frete >= 5:
        return "frete_peso"
    elif match_abrang >= 5:
        return "abrangencia"
    else:
        return "desconhecido"

def normalizar_colunas(df, colunas_modelo):
    df_corrigido = pd.DataFrame()
    for col in colunas_modelo:
        if col in df.columns:
            df_corrigido[col] = df[col]
        else:
            df_corrigido[col] = ""
    return df_corrigido

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        tipo = detectar_tipo(df.columns)

        if tipo == "frete_peso":
            df_final = normalizar_colunas(df, template_frete_peso)
            nome_saida = "frete_peso_tower.csv"
        elif tipo == "abrangencia":
            df_final = normalizar_colunas(df, template_abrangencia)
            nome_saida = "abrangencia_tower.csv"
        else:
            st.error("❌ Não foi possível identificar se a planilha é do tipo 'frete/peso' ou 'abrangência'.")
            st.stop()

        st.success(f"✅ Tabela do tipo **{tipo}** reconhecida e convertida com sucesso!")

        st.download_button(
            label="📥 Baixar CSV Convertido",
            data=df_final.to_csv(index=False).encode("utf-8"),
            file_name=nome_saida,
            mime="text/csv"
        )

        st.dataframe(df_final)

    except Exception as e:
        st.error("⚠️ Erro ao processar a planilha:")
        st.exception(e)
