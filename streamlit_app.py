
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conversor Tower", layout="centered")
st.title("📦 Conversor de Tabelas para o Tower")

uploaded_file = st.file_uploader(
    "Faça upload da planilha (.csv, .xls ou .xlsx)",
    type=["csv", "xls", "xlsx"]
)

st.caption("💡 Dica: se o upload de .xlsx falhar, salve como .csv e tente novamente.")

map_frete = {
    "transportadora": "CARRIER",
    "uf origem": "ORIGIN_UF",
    "região": "REGION",
    "peso inicial": "WEIGHTSTART",
    "peso final": "WEIGHTEND",
    "preço": "PRICE",
    "cidade origem": "ORIGIN_CITY",
    "nível": "TIER",
    "início vigência": "VIGENCIASTART",
    "fim vigência": "VIGENCIAEND"
}
map_abrang = {
    "uf origem": "origin_uf",
    "cidade origem": "origin_city",
    "estado destino": "state",
    "cidade destino": "city",
    "cep inicial": "zip_code_start",
    "cep final": "zip_code_end",
    "prazo": "slo",
    "região": "region",
    "gris": "gris",
    "ad valorem": "advalorem",
    "etiqueta": "shipping_label",
    "início vigência": "date_start",
    "fim vigência": "date_end"
}

template_frete = list(map_frete.values())
template_abrang = list(map_abrang.values())

def normalizar_nome(col):
    return col.strip().lower().replace(":", "").replace("  ", " ")

def detectar_tipo_por_mapeamento(colunas):
    nomes = [normalizar_nome(str(c)) for c in colunas]
    mapped = [map_frete.get(n) for n in nomes if n in map_frete] + [map_abrang.get(n) for n in nomes if n in map_abrang]
    match_frete = len([c for c in mapped if c in template_frete])
    match_abrang = len([c for c in mapped if c in template_abrang])
    if match_frete >= 5:
        return "frete_peso"
    elif match_abrang >= 5:
        return "abrangencia"
    else:
        return "desconhecido"

def mapear_colunas(df, tipo):
    mapa = map_frete if tipo == "frete_peso" else map_abrang
    template = template_frete if tipo == "frete_peso" else template_abrang
    colunas_map = {}
    for col in df.columns:
        nome_limpo = normalizar_nome(str(col))
        if nome_limpo in mapa:
            colunas_map[mapa[nome_limpo]] = col
    df_padrao = pd.DataFrame()
    for col in template:
        if col in colunas_map:
            df_padrao[col] = df[colunas_map[col]]
        else:
            df_padrao[col] = ""
    return df_padrao

if uploaded_file:
    try:
        ext = uploaded_file.name.split(".")[-1]
        df_convertido, tipo = None, "desconhecido"

        if ext == "csv":
            df = pd.read_csv(uploaded_file)
            tipo = detectar_tipo_por_mapeamento(df.columns)
            if tipo != "desconhecido":
                df_convertido = mapear_colunas(df, tipo)
        else:
            xl = pd.ExcelFile(uploaded_file)
            for aba in xl.sheet_names:
                df_teste = pd.read_excel(uploaded_file, sheet_name=aba, nrows=10)
                tipo_detectado = detectar_tipo_por_mapeamento(df_teste.columns)
                if tipo_detectado != "desconhecido":
                    df_raw = pd.read_excel(uploaded_file, sheet_name=aba)
                    df_convertido = mapear_colunas(df_raw, tipo_detectado)
                    tipo = tipo_detectado
                    break

        if tipo == "desconhecido" or df_convertido is None:
            st.error("❌ Não conseguimos reconhecer o tipo da planilha.")
            st.stop()

        st.success("✅ Planilha reconhecida e convertida com sucesso!")
        nome_saida = f"tower_{tipo}.csv"
        st.download_button("📥 Baixar CSV Convertido", df_convertido.to_csv(index=False).encode("utf-8"), file_name=nome_saida, mime="text/csv")
        st.dataframe(df_convertido)

    except Exception as e:
        st.error("⚠️ Erro ao processar a planilha:")
        st.exception(e)
