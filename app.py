import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Separador de Coordenadas", layout="wide")

st.title("Separador de Latitude e Longitude em Planilhas")

st.markdown("""
Esta aplicação permite extrair e separar automaticamente as colunas de **latitude** e **longitude** presentes em uma planilha Excel.  
Basta enviar um arquivo `.xlsx` contendo uma coluna de coordenadas (por exemplo, no formato `-13,181564765 | -60,87444104`) e o app irá processar, separar e disponibilizar as informações geográficas em colunas próprias.  
Ideal para quem precisa padronizar, analisar ou visualizar dados georreferenciados de forma rápida e sem erros manuais.
""")

# 1. Upload do arquivo
uploaded_file = st.file_uploader("Faça upload do arquivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    # 2. Leitura da planilha
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.stop()
    
    # 3. Identificação automática da coluna de coordenadas
    colunas_normalizadas = {col.lower().strip(): col for col in df.columns}
    possiveis_nomes = ['coordenadas', 'coord', 'coordenadas gps', 'COORDENADAS', 'COORDENADAS GPS']
    col_coordenadas = None
    for nome in possiveis_nomes:
        if nome in colunas_normalizadas:
            col_coordenadas = colunas_normalizadas[nome]
            break
    if col_coordenadas is None:
        st.error("Coluna de coordenadas não encontrada! Certifique-se que existe uma coluna chamada 'coordenadas'.")
        st.stop()
    
    # 4. Limpeza e separação das coordenadas
    df[col_coordenadas] = df[col_coordenadas].astype(str).str.strip().str.replace('\n', '', regex=True)
    df[['latitude', 'longitude']] = df[col_coordenadas].str.split('|', expand=True)
    df['latitude'] = df['latitude'].str.strip().str.replace(',', '.')
    df['longitude'] = df['longitude'].str.strip().str.replace(',', '.')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df.drop(columns=[col_coordenadas], inplace=True)
    
    st.success("Colunas separadas com sucesso!")
    st.subheader("Prévia dos dados:")
    st.dataframe(df.head(10))

    # 5. Opções de download
    st.subheader("Baixar arquivo corrigido")
    formato = st.selectbox(
        "Escolha o formato de exportação:",
        [".csv (vírgula)", ".csv (ponto e vírgula)", ".csv (UTF-8 BOM)", ".xlsx (Excel)"]
    )

    if formato == ".csv (vírgula)":
        csv = df.to_csv(index=False, encoding='utf-8')
        st.download_button("Baixar CSV (vírgula)", csv, "planilha_corrigida.csv", "text/csv")
    elif formato == ".csv (ponto e vírgula)":
        csv = df.to_csv(index=False, sep=';', encoding='utf-8')
        st.download_button("Baixar CSV (ponto e vírgula)", csv, "planilha_corrigida_pt_virgula.csv", "text/csv")
    elif formato == ".csv (UTF-8 BOM)":
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("Baixar CSV (UTF-8 BOM)", csv, "planilha_corrigida_utf8bom.csv", "text/csv")
    elif formato == ".xlsx (Excel)":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            label="Baixar Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="planilha_corrigida.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Faça upload de um arquivo Excel (.xlsx) para começar.")
