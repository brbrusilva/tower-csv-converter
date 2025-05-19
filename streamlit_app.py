
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Agente de Conversão Tower", layout="centered")
st.title("🤖 Conversor Inteligente de Planilhas para o Tower")

uploaded_file = st.file_uploader(
    "Faça upload da planilha (.csv, .xls ou .xlsx)",
    type=["csv", "xls", "xlsx"]
)

map_frete = {
    "transportadora": "CARRIER",
    "uf origem": "ORIGIN_UF",
    "região": "REGION",
    "peso inicial": "WEIGHTSTART",
    "peso final": "WEIGHTEND",
    "preço": "PRICE",
    "valor": "PRICE",
    "valor r$": "PRICE",
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
    return col.strip().lower().replace(":", "").replace("  ", " ").replace("r$", "valor")

def detectar_tipo_por_colunas(colunas):
    nomes = [normalizar_nome(str(c)) for c in colunas]
    frete_detect = [map_frete.get(n) for n in nomes if n in map_frete]
    abrang_detect = [map_abrang.get(n) for n in nomes if n in map_abrang]
    return frete_detect, abrang_detect

def mapear_colunas(df, tipo):
    mapa = map_frete if tipo == "frete_peso" else map_abrang
    template = template_frete if tipo == "frete_peso" else template_abrang
    colunas_map = {}
    colunas_reconhecidas = []
    colunas_originais = list(df.columns)

    for col in colunas_originais:
        nome_limpo = normalizar_nome(str(col))
        if nome_limpo in mapa:
            colunas_map[mapa[nome_limpo]] = col
            colunas_reconhecidas.append(col)

    df_padrao = pd.DataFrame()
    for col in template:
        if col in colunas_map:
            df_padrao[col] = df[colunas_map[col]]
        else:
            df_padrao[col] = ""

    colunas_nao_usadas = [c for c in colunas_originais if c not in colunas_reconhecidas]

    return df_padrao, colunas_reconhecidas, colunas_nao_usadas

def encontrar_linha_e_tipo(df):
    for i in range(min(len(df), 200)):
        tentativa = df.iloc[i].tolist()
        frete, abrang = detectar_tipo_por_colunas(tentativa)
        if len(frete) >= 5:
            return i, "frete_peso"
        elif len(abrang) >= 5:
            return i, "abrangencia"
    return None, "desconhecido"

if uploaded_file:
    try:
        ext = uploaded_file.name.split(".")[-1]
        df_convertido, tipo = None, "desconhecido"

        if ext == "csv":
            df_raw = pd.read_csv(uploaded_file, header=None)
            linha_cab, tipo = encontrar_linha_e_tipo(df_raw)
            if linha_cab is not None:
                df = pd.read_csv(uploaded_file, header=linha_cab)
                df_convertido, usadas, ignoradas = mapear_colunas(df, tipo)
        else:
            xl = pd.ExcelFile(uploaded_file)
            for aba in xl.sheet_names:
                df_raw = pd.read_excel(uploaded_file, sheet_name=aba, header=None, nrows=200)
                linha_cab, tipo_detectado = encontrar_linha_e_tipo(df_raw)
                if linha_cab is not None:
                    df = pd.read_excel(uploaded_file, sheet_name=aba, header=linha_cab)
                    df_convertido, usadas, ignoradas = mapear_colunas(df, tipo_detectado)
                    tipo = tipo_detectado
                    break

        if tipo == "desconhecido" or df_convertido is None:
            st.error("❌ Não conseguimos reconhecer o tipo da planilha.")
            st.info("""💡 Sugestões:
- Verifique se as colunas têm nomes como 'CEP inicial', 'Preço (R$)', 'Cidade origem'
- Inclua ao menos 5 colunas comuns ao padrão Tower""")
            st.stop()

        st.success(f"✅ Planilha identificada como tipo '{tipo.replace('_', ' ')}' e convertida com sucesso!")
        st.markdown("### ✅ Colunas reconhecidas:")
        st.markdown(", ".join(usadas))

        if ignoradas:
            st.markdown("### ⚠️ Colunas ignoradas (não fazem parte do modelo):")
            st.markdown(", ".join(ignoradas))

        nome_saida = f"tower_{tipo}.csv"
        st.download_button("📥 Baixar CSV Convertido", df_convertido.to_csv(index=False).encode("utf-8"), file_name=nome_saida, mime="text/csv")
        st.dataframe(df_convertido)

    except Exception as e:
        st.error("⚠️ Erro ao processar a planilha:")
        st.exception(e)
